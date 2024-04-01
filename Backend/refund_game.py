from flask import Flask, request, jsonify
from invokes import invoke_http
from flask_cors import CORS
import pika
import amqp_connection
import os, sys
import json
from itertools import combinations

app = Flask(__name__)
CORS(app)

# Define the microservices URLs
USER_MICROSERVICE_URL = "http://user:5600"
PAYMENT_MICROSERVICE_URL = "http://payment:5604"
ERROR_MICROSERVICE_URL = "http://error:5445/error"
SHOP_MICROSERVICE_URL = "http://shop:5601"

# amqp stuff
exchangename = "order_topic"  # exchange name
exchangetype = "topic"  # use a 'topic' exchange to enable interaction
connection = amqp_connection.create_connection()
channel = connection.channel()

# # if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print(
        "\nCreate the 'Exchange' before running this microservice. \nExiting the program."
    )
    sys.exit(0)  # Exit with a success status

def process_refund_notification(notification_json):
    message = notification_json

    print(
        "\n\n-----Publishing the notification with routing_key=refund.notification-----"
    )

    try:
        channel.basic_publish(
            exchange=exchangename,
            routing_key="refund.notification",
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
       
    # make message persistent within the matching queues

    # - reply from the invocation is not used;
    # continue even if this invocation fails
    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = (
            str(e)
            + " at "
            + str(exc_type)
            + ": "
            + fname
            + ": line "
            + str(exc_tb.tb_lineno)
        )
        print(ex_str)


@app.route("/refund-game", methods=["POST"])
def process_refund():
    # Pull data first
    
    if request.is_json:
        try:
            data = request.get_json()
            user_id = data["user_id"]
            game_id = data["game_id"]

            # Retrieve user's gameplay time and purchase id
            print("-----Invoking user microservice-----")
            game_purchase_details_result = invoke_http(
                f"{USER_MICROSERVICE_URL}/users/game-purchase?userId={user_id}&gameId={game_id}",
                method="GET"
            )
            print("game_purchase_details_result:", game_purchase_details_result, "\n")

            game_purchase_details_result_code = game_purchase_details_result["code"]
            game_purchase_details_message = json.dumps(game_purchase_details_result)
 
            if game_purchase_details_result_code not in range(200, 300):
                print('\n\n-----Publishing the (game purchase details error) message with routing_key=game.purchase.details.error-----')

                channel.basic_publish(exchange=exchangename, routing_key="game.purchase.details.error", 
                    body=game_purchase_details_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                # make message persistent within the matching queues 

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nGame purchase details status ({:d}) published to the RabbitMQ Exchange:".format(
                    game_purchase_details_result_code), game_purchase_details_result)
                
                result = {
                    "code": 500,
                    "data": {
                        "game_purchase_details_result": game_purchase_details_result
                    },
                    "message": "Game purchase creation error sent for error handling"
                }

                print('\n------------------------')
                print('\nresult: ', result)
                return jsonify(result), result["code"]
            
            gameplay_time = game_purchase_details_result["data"]["gameplay_time"]
            purchase_id = game_purchase_details_result["data"]["payment_intent"]


            # Check for refund eligibility, publish error if gameplay time > 120 mins
            if gameplay_time and gameplay_time >= 120:
                result = {
                    "code": 400,
                    "message": "Refund cannot be processed as the gameplay time exceeds 120 minutes"
                }

                print('\n\n-----Publishing the (gameplay time error) message with routing_key=gameplay.time.error-----')

                channel.basic_publish(exchange=exchangename, routing_key="gameplay.time.error", 
                    body=json.dumps(result), properties=pika.BasicProperties(delivery_mode = 2)) 
                # make message persistent within the matching queues 

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nGameplay time status ({:d}) published to the RabbitMQ Exchange:".format(
                    result["code"]), result)
            
                print('\n------------------------')
                print('\nresult: ', result)
                return jsonify(result), result["code"]
            

            # Get game points awarded
            print("-----Invoking shop microservice-----")
            game_details_result = invoke_http(
                f"{SHOP_MICROSERVICE_URL}/shop/games/{game_id}", method="GET"
            )
            print("game_details_result:", game_details_result, "\n")

            game_details_message = json.dumps(game_details_result)

            if game_details_result["code"] not in range(200, 300):
                print(
                    "\n\n-----Publishing the (game details error) message with routing_key=game.details.error-----"
                )

                channel.basic_publish(
                    exchange=exchangename,
                    routing_key="game.details.error",
                    body=game_details_message,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                # make message persistent within the matching queues

                # - reply from the invocation is not used;
                # continue even if this invocation fails
                print(
                    "\nGame details status ({:d}) published to the RabbitMQ Exchange:".format(
                        game_details_result["code"]
                    ),
                    game_details_result
                )

                result = {
                    "code": 500,
                    "data": { "game_details_result": game_details_result },
                    "message": "Game details error sent for error handling",
                }

                print('\n------------------------')
                print('\nresult: ', result)
                return jsonify(result), result["code"]

            points_to_deduct = game_details_result["data"]["points"]
            
            
            # Get user points
            print("-----Invoking user microservice-----")
            user_details_result = invoke_http(
                f"{USER_MICROSERVICE_URL}/users/{user_id}", method="GET"
            )
            print("user_details_result:", user_details_result, "\n")

            user_details_result_code = user_details_result['code']
            user_details_message = json.dumps(user_details_result)

            if user_details_result_code not in range(200, 300):
                print('\n\n-----Publishing the (user details error) message with routing_key=user.details.error-----')

                channel.basic_publish(exchange=exchangename, routing_key="user.details.error", 
                    body=user_details_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                # make message persistent within the matching queues 

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nUser details status ({:d}) published to the RabbitMQ Exchange:".format(
                    user_details_result_code), user_details_result)
                
                result = {
                    "code": 500,
                    "data": {
                        "user_details_result": user_details_result
                    },
                    "message": "User details error sent for error handling"
                }

                print('\n------------------------')
                print('\nresult: ', result)
                return jsonify(result), result["code"]
        
            user_points = user_details_result["data"]["points"]


            # Check if points are sufficient
            if user_points >= points_to_deduct:
                points_to_change = {
                    "user_id": user_id,
                    "price": points_to_deduct / 100,
                    "operation": "subtract"
                }

                # invoke user.py endpoint that only updates the points
                print("-----Invoking user microservice-----")
                update_points_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/points/update",
                    method="PUT",
                    json=points_to_change,
                )
                print("update_points_result:", update_points_result)

                update_points_result_code = update_points_result["code"]
                update_points_message = json.dumps(update_points_result)

                if update_points_result_code not in range(200, 300):
                    print('\n\n-----Publishing the (points update error) message with routing_key=points.update.error-----')

                    channel.basic_publish(exchange=exchangename, routing_key="points.update.error", 
                        body=update_points_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues 

                    # - reply from the invocation is not used;
                    # continue even if this invocation fails        
                    print("\nPoints update status ({:d}) published to the RabbitMQ Exchange:".format(
                        update_points_result_code), update_points_result)

                    result = {
                        "code": 500,
                        "data": {
                            "update_points_result": update_points_result
                        },
                        "message": "Points update error sent for error handling"
                    }

                    print('\n------------------------')
                    print('\nresult: ', result)
                    return jsonify(result), result["code"]
            else:
                points_to_deduct_from_customizations = points_to_deduct - user_points

                # Get user customizations
                print("-----Invoking user microservice-----")
                user_customizations_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/{user_id}/customizations",
                    method="GET",
                )
                print("user_customizations_result: ", user_customizations_result, '\n')

                user_customizations_result_code = user_customizations_result["code"]
                user_customizations_message = json.dumps(user_customizations_result)
                
                # error handle if cant retrieve
                if user_customizations_result_code not in range(200, 300):
                    print('\n\n-----Publishing the (user customizations error) message with routing_key=user.customizations.error-----')

                    channel.basic_publish(exchange=exchangename, routing_key="user.customizations.error", 
                        body=user_customizations_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues 

                    # - reply from the invocation is not used;
                    # continue even if this invocation fails        
                    print("\nUser customizations status ({:d}) published to the RabbitMQ Exchange:".format(
                        user_customizations_result_code), user_customizations_result)
                    
                    result = {
                        "code": 500,
                        "data": {
                            "user_customizations_result": user_customizations_result
                        },
                        "message": "User customizations error sent for error handling"
                    }

                    print('\n------------------------')
                    print('\nresult: ', result)
                    return jsonify(result), result["code"]

                user_customizations_result_list = user_customizations_result["data"]


                # Get all customizations
                print("-----Invoking shop microservice-----")
                customizations_result = invoke_http(
                    f"{SHOP_MICROSERVICE_URL}/shop/customizations",
                    method="GET"
                )
                print("customizations_result:", customizations_result, "\n")

                customizations_result_code = customizations_result["code"]
                customizations_message = json.dumps(customizations_result)

                # error handle if cant retrieve
                if customizations_result_code not in range(200, 300):
                    print('\n\n-----Publishing the (customizations error) message with routing_key=customizations.error-----')

                    channel.basic_publish(exchange=exchangename, routing_key="customizations.error", 
                        body=customizations_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues 

                    # - reply from the invocation is not used;
                    # continue even if this invocation fails        
                    print("\nCustomizations status ({:d}) published to the RabbitMQ Exchange:".format(
                        customizations_result_code), customizations_result)
                    
                    result = {
                        "code": 500,
                        "data": {
                            "customizations_result": customizations_result
                        },
                        "message": "Customizations error sent for error handling"
                    }

                    print('\n------------------------')
                    print('\nresult: ', result)
                    return jsonify(result), result["code"]

                customizations_list = customizations_result["data"]["customizations"]
                customizations_dict = {}

                for customization in customizations_list:
                    customizations_dict[customization["customization_id"]] = (
                        customization["credits"]
                    )

                possible_user_customizations_to_remove = []

                for customization in user_customizations_result_list:
                    customization_tuple = (
                        customization["customization_id"],
                        customizations_dict[customization["customization_id"]],
                    )
                    possible_user_customizations_to_remove.append(customization_tuple)

                to_remove_list = []

                # while points_to_deduct_from_customizations > 0 and len(possible_user_customizations_to_remove) > 0:
                #     possible_user_customizations_to_remove_points = possible_user_customizations_to_remove[-1][1]

                #     if possible_user_customizations_to_remove_points > points_to_deduct_from_customizations:
                #         possible_user_customizations_to_remove.pop()
                #         continue

                #     points_to_deduct_from_customizations -= possible_user_customizations_to_remove_points
                #     user_customization = possible_user_customizations_to_remove.pop()
                #     to_remove_list.append(user_customization[0])

                isBestCombination = False
                # Best case scenario
                for customization_tuple in possible_user_customizations_to_remove:
                    customization_points = customization_tuple[1]
                    if customization_points == points_to_deduct_from_customizations:
                        to_remove_list.append(customization_tuple[0])
                        points_to_deduct_from_customizations = 0
                        isBestCombination = True
                        break

                isSufficientForRefund = True
                compensate_points = 0
                if not isBestCombination:
                    total_points = 0

                    # Check if user customizations are sufficient for refund
                    for customization_tuple in possible_user_customizations_to_remove:
                        customization_points = customization_tuple[1]
                        total_points += customization_points
                        to_remove_list.append(customization_tuple[0])

                    if total_points < points_to_deduct_from_customizations:
                        isSufficientForRefund = False

                    elif total_points == points_to_deduct_from_customizations:
                        points_to_deduct_from_customizations = 0

                    elif total_points != points_to_deduct_from_customizations:
                        # Reset
                        to_remove_list = []

                        temp_to_remove_list = []
                        
                        combs = list(combinations(possible_user_customizations_to_remove, 2))

                        # Initialize first combination
                        smallest_eligible_points_diff = float('inf')

                        for comb in combs:
                            comb_total_points = comb[0][1] + comb[1][1]
                            points_diff = comb_total_points - points_to_deduct_from_customizations

                            if points_diff < smallest_eligible_points_diff and points_diff >= 0:
                                # Reset
                                temp_to_remove_list.clear()

                                temp_to_remove_list.append(comb)
                                smallest_eligible_points_diff = points_diff

                        for customization in possible_user_customizations_to_remove:
                            customization_points = customization[1]
                            points_diff = customization_points - points_to_deduct_from_customizations

                            if points_diff < smallest_eligible_points_diff and points_diff >= 0:
                                # Reset
                                temp_to_remove_list.clear()

                                temp_to_remove_list.append(customization)
                                smallest_eligible_points_diff = points_diff

                        # Special handling (can't use len())
                        if str(temp_to_remove_list).count(",") == 3:
                            to_remove_customizations = temp_to_remove_list[0]
                            to_remove_list.append(to_remove_customizations[0][0])
                            to_remove_list.append(to_remove_customizations[1][0])
                            to_remove_list_total_points = to_remove_customizations[0][1] + to_remove_customizations[1][1]

                            # If refunded customization credits > points_to_deduct_from_customizations, compensate the user
                            if to_remove_list_total_points > points_to_deduct_from_customizations:
                                compensate_points += to_remove_list_total_points - points_to_deduct_from_customizations

                        elif len(temp_to_remove_list) == 1:
                            to_remove_customization = temp_to_remove_list[0]
                            to_remove_list.append(to_remove_customization[0])
                            to_remove_list_total_points = to_remove_customization[1]

                            # If refunded customization credits > points_to_deduct_from_customizations, compensate the user
                            if to_remove_list_total_points > points_to_deduct_from_customizations:
                                compensate_points += to_remove_list_total_points - points_to_deduct_from_customizations

                        points_to_deduct_from_customizations = 0

                # If user customizations are insufficient for refund
                if not isSufficientForRefund:
                    result = {
                        "code": 400,
                        "message": "Refund cannot be processed as user customizations are insufficient for refund"
                    }

                    print('\n\n-----Publishing the (customizations refund error) message with routing_key=customizations.refund.error-----')

                    channel.basic_publish(exchange=exchangename, routing_key="customizations.refund.error", 
                        body=json.dumps(result), properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues 

                    # - reply from the invocation is not used;
                    # continue even if this invocation fails        
                    print("\nCustomizations refund status ({:d}) published to the RabbitMQ Exchange:".format(
                        result["code"]), result)
            
                    print('\n------------------------')
                    print('\nresult: ', result)
                    return jsonify(result), result["code"]
                    
                change_points = user_points - points_to_deduct_from_customizations - compensate_points


                # Delete user customizations
                customizations_to_delete = {
                    "user_id": user_id,
                    "to_remove_list": to_remove_list,
                }

                print("-----Invoking user microservice-----")
                delete_customizations_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/customizations/delete",
                    method="DELETE",
                    json=customizations_to_delete,
                )
                print("delete_customizations_result:", delete_customizations_result, "\n")

                delete_customizations_result_code = delete_customizations_result["code"]
                delete_customizations_message = json.dumps(delete_customizations_result)

                # error handle if cant retrieve
                if delete_customizations_result_code not in range(200, 300):
                    print('\n\n-----Publishing the (delete customizations error) message with routing_key=customizations.deletion.error-----')

                    channel.basic_publish(exchange=exchangename, routing_key="customizations.deletion.error", 
                        body=delete_customizations_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues 

                    # - reply from the invocation is not used;
                    # continue even if this invocation fails        
                    print("\nCustomizations deletion status ({:d}) published to the RabbitMQ Exchange:".format(
                        delete_customizations_result_code), delete_customizations_result)
                    
                    result = {
                        "code": 500,
                        "data": {
                            "delete_customizations_result_result": delete_customizations_result
                        },
                        "message": "Customizations deletion error sent for error handling"
                    }

                    print('\n------------------------')
                    print('\nresult: ', result)
                    return jsonify(result), result["code"]


                # Update user points
                points_to_change = {
                    "user_id": user_id,
                    "price": abs(change_points / 100),
                    "operation": "subtract",
                }

                print("-----Invoking user microservice-----")
                update_points_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/points/update",
                    method="PUT",
                    json=points_to_change,
                )
                print("update_points_result:", update_points_result, "\n")

                update_points_result_code = update_points_result["code"]
                update_points_message = json.dumps(update_points_result)

                # error handle if cant retrieve
                if update_points_result_code not in range(200, 300):
                    print('\n\n-----Publishing the (points update error) message with routing_key=points.update.error-----')

                    channel.basic_publish(exchange=exchangename, routing_key="points.update.error", 
                        body=update_points_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues 

                    # - reply from the invocation is not used;
                    # continue even if this invocation fails        
                    print("\nPoints update status ({:d}) published to the RabbitMQ Exchange:".format(
                        update_points_result_code), update_points_result)

                    result = {
                        "code": 500,
                        "data": {
                            "update_points_result": update_points_result
                        },
                        "message": "Points update error sent for error handling"
                    }

                    print('\n------------------------')
                    print('\nresult: ', result)
                    return jsonify(result), result["code"]

            # Delete purchase record
            del_json = {"user_id": user_id, "game_id": game_id}
            
            print("-----Invoking user microservice-----")
            delete_game_purchase_result = invoke_http(
                f"{USER_MICROSERVICE_URL}/users/game-purchase/delete",
                method="DELETE",
                json=del_json,
            )
            print("delete_game_purchase_result:", delete_game_purchase_result, "\n")

            delete_game_purchase_result_code = delete_game_purchase_result["code"]
            delete_game_purchase_message = json.dumps(delete_game_purchase_result)

            # error handle if cant retrieve
            if delete_game_purchase_result_code not in range(200, 300):
                print('\n\n-----Publishing the (game purchase deletion error) message with routing_key=game.purchase.deletion.error-----')

                channel.basic_publish(exchange=exchangename, routing_key="game.purchase.deletion.error", 
                    body=delete_game_purchase_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                # make message persistent within the matching queues 

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nGame purchase deletion status ({:d}) published to the RabbitMQ Exchange:".format(
                    delete_game_purchase_result_code), delete_game_purchase_result)
                
                result = {
                    "code": 500,
                    "data": {
                        "delete_game_purchase_result": delete_game_purchase_result
                    },
                    "message": "Game purchase deletion error sent for error handling"
                }

                print('\n------------------------')
                print('\nresult: ', result)
                return jsonify(result), result["code"]
            

            # Process the refund through Stripe
            payment_intent_id = purchase_id
            payment_refund_data = {"payment_intent": payment_intent_id}

            print('\n-----Invoking payment microservice-----')
            payment_refund_result = invoke_http(
                f"{PAYMENT_MICROSERVICE_URL}/refund", method="POST", json=payment_refund_data
            )
            print('payment_refund_result:', payment_refund_result, '\n')

            payment_refund_result_code = payment_refund_result["code"]
            payment_refund_message = json.dumps(payment_refund_result)

            if payment_refund_result_code not in range(200, 300):
                print('\n\n-----Publishing the (payment refund error) message with routing_key=payment.refund.error-----')

                channel.basic_publish(exchange=exchangename, routing_key="payment.refund.error", 
                    body=payment_refund_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                # make message persistent within the matching queues 

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nPayment refund status ({:d}) published to the RabbitMQ Exchange:".format(
                    payment_refund_result_code), payment_refund_result)
                
                result = {
                    "code": 500,
                    "data": {
                        "payment_refund_result": payment_refund_result
                    },
                    "message": "Refund error sent for error handling"
                }

                print('\n------------------------')
                print('\nresult: ', result)
                return jsonify(result), result["code"]

            # Step 7: Send email notification to user
            notification_json = {
                "game_price": game_details_result["data"]["price"],
                "game_title": game_details_result["data"]["title"],
                "email": user_details_result["data"]["email"],
                "account_name": user_details_result["data"]["account_name"],
                "purchase_id": payment_intent_id,
            }

            print("processing notification...")
            process_refund_notification(notification_json)

            result = {
                "code": 200,
                "data": {
                    "update_points_result": update_points_result,
                    "payment_refund_result": payment_refund_result
                },
                "message": "Refund error sent for error handling"
            }

            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]
        
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "refund_game.py internal error"
                }
            ), 500
        
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5606, debug=True)
