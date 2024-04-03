from flask import Flask, request, jsonify
from invokes import invoke_http
from flask_cors import CORS
from flasgger import Swagger

import pika
import amqp_connection
import os, sys
import json
from itertools import combinations

app = Flask(__name__)
CORS(app)

# Initialize flasgger for API Documentation
app.config['SWAGGER'] = {
    'title': 'Shop microservice API',
    'version': 2.0,
    "openapi": "3.0.2",
    'description': 'Allows create, retrieve, update, and delete of shop items',
    'tags': {
        'Games': 'Operations related to game management',
        'Customizations': 'Operations related to customizations',
    },
    'ui_params': {
        'apisSorter': 'alpha',
        'operationsSorter': 'alpha',
        'tagsSorter': 'alpha',
    },
    'ui_params_text': '''{
        "tagsSorter": (a, b) => {
            const order = ['Users', 'Customisations'];
            return order.indexOf(a) - order.indexOf(b);
        }
    }''',
    
}

swagger = Swagger(app)

# Define the microservices URLs
USER_MICROSERVICE_URL = "http://kong:8000"
PAYMENT_MICROSERVICE_URL = "http://kong:8000"
ERROR_MICROSERVICE_URL = "http://kong:8000/error"
SHOP_MICROSERVICE_URL = "http://kong:8000"

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

    # try:
    channel.basic_publish(
        exchange=exchangename,
        routing_key="refund.notification",
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )
       
    # make message persistent within the matching queues

    # - reply from the invocation is not used;
    # continue even if this invocation fails
    # except Exception as e:
    #     # Unexpected error in code
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     ex_str = (
    #         str(e)
    #         + " at "
    #         + str(exc_type)
    #         + ": "
    #         + fname
    #         + ": line "
    #         + str(exc_tb.tb_lineno)
    #     )
    #     print(ex_str)


@app.route("/refund-game", methods=["POST"])
def process_refund():
    # Pull data first
    
    if request.is_json:
        try:
            data = request.get_json()
            user_id = data["user_id"]
            game_id = data["game_id"]

            # Technical robustness
            num_retries = 0
            max_retries = 5

            shouldRetry = True

            game_purchase_details_result = {}
            game_purchase_details_result_code = 400
            game_purchase_details_message = ""

            game_details_result = {}
            game_details_result_code = 400
            game_details_message = ""

            user_details_result = {}
            user_details_result_code = 400
            user_details_message = ""

            update_points_result = {}
            update_points_result_code = 400
            update_points_message = ""

            user_customizations_result = {}
            user_customizations_result_code = 400
            user_customizations_message = ""

            customizations_result = {}
            customizations_result_code = 400
            customizations_message = ""

            delete_customizations_result = {}
            delete_customizations_result_code = 400
            delete_customizations_message = ""

            update_user_details_result = {}
            update_user_details_result_code = 400
            update_user_details_message = ""

            delete_game_purchase_result = {}
            delete_game_purchase_result_code = 400
            delete_game_purchase_message = ""

            payment_refund_result = {}
            payment_refund_result_code = 400
            payment_refund_message = ""

            # Retrieve user's gameplay time and purchase id
            while num_retries < max_retries and game_purchase_details_result_code not in range(200, 300) and shouldRetry == True:
                print("-----Invoking user microservice-----")
                game_purchase_details_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/game-purchase?userId={user_id}&gameId={game_id}",
                    method="GET"
                )
                print("game_purchase_details_result:", game_purchase_details_result, "\n")

                if "message" in game_purchase_details_result and len(game_purchase_details_result) == 2 and "Invalid query" not in game_purchase_details_result["message"]:
                    shouldRetry = True

                    if num_retries + 1 == max_retries:
                        game_purchase_details_message = json.dumps(game_purchase_details_result)
                else: 
                    shouldRetry = False
                    game_purchase_details_result_code = game_purchase_details_result["code"]
                    game_purchase_details_message = json.dumps(game_purchase_details_result)
                    
                num_retries += 1

            # Reset
            shouldRetry = True
            num_retries = 0

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
            while num_retries < max_retries and game_details_result_code not in range(200, 300) and shouldRetry == True:
                print("-----Invoking shop microservice-----")
                game_details_result = invoke_http(
                    f"{SHOP_MICROSERVICE_URL}/shop/games/{game_id}", method="GET"
                )
                print("game_details_result:", game_details_result, "\n")

                if "message" in game_details_result and len(game_details_result) == 2:
                    shouldRetry = True

                    if num_retries + 1 == max_retries:
                        game_details_message = json.dumps(game_details_result)
                else: 
                    shouldRetry = False
                    game_details_result_code = game_details_result["code"]
                    game_details_message = json.dumps(game_details_result)

                num_retries += 1

            # Reset
            shouldRetry = True
            num_retries = 0

            if game_details_result_code not in range(200, 300):
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
                        game_details_result_code
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
            while num_retries < max_retries and user_details_result_code not in range(200, 300) and shouldRetry == True:
                print("-----Invoking user microservice-----")
                user_details_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/{user_id}", method="GET"
                )
                print("user_details_result:", user_details_result, "\n")

                if "message" in user_details_result and len(user_details_result) == 2:
                    shouldRetry = True
                    
                    if num_retries + 1 == max_retries:
                        user_details_message = json.dumps(user_details_result)
                else: 
                    shouldRetry = False
                    user_details_result_code = user_details_result['code']
                    user_details_message = json.dumps(user_details_result)

                num_retries += 1

            # Reset
            shouldRetry = True
            num_retries = 0

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
                    "points": points_to_deduct / 100,
                    "operation": "subtract"
                }

                # invoke user.py endpoint that only updates the points
                while num_retries < max_retries and update_points_result_code not in range(200, 300) and shouldRetry == True:
                    print("-----Invoking user microservice-----")
                    update_points_result = invoke_http(
                        f"{USER_MICROSERVICE_URL}/users/" + str(user_id) + "/update",
                        method="PUT",
                        json=points_to_change,
                    )
                    print("update_points_result:", update_points_result, "\n")

                    if "message" in update_points_result and len(update_points_result) == 2 and "Invalid JSON input" not in update_points_result["message"]:
                        shouldRetry = True

                        if num_retries + 1 == max_retries:
                            update_points_message = json.dumps(update_points_result)
                    else: 
                        shouldRetry = False
                        update_points_result_code = update_points_result["code"]
                        update_points_message = json.dumps(update_points_result)

                    num_retries += 1

                # Reset
                shouldRetry = True
                num_retries = 0

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
                while num_retries < max_retries and user_customizations_result_code not in range(200, 300) and shouldRetry == True:
                    print("-----Invoking user microservice-----")
                    user_customizations_result = invoke_http(
                        f"{USER_MICROSERVICE_URL}/users/{user_id}/customization-purchase",
                        method="GET",
                    )
                    print("user_customizations_result: ", user_customizations_result, '\n')

                    if "message" in user_customizations_result and len(user_customizations_result) == 2:
                        shouldRetry = True
                        if num_retries + 1 == max_retries:
                            user_customizations_message = json.dumps(user_customizations_result)
                    else: 
                        shouldRetry = False
                        user_customizations_result_code = user_customizations_result["code"]
                        user_customizations_message = json.dumps(user_customizations_result)
        
                    num_retries += 1

                # Reset
                shouldRetry = True
                num_retries = 0

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
                while num_retries < max_retries and customizations_result_code not in range(200, 300) and shouldRetry == True:
                    print("-----Invoking shop microservice-----")
                    customizations_result = invoke_http(
                        f"{SHOP_MICROSERVICE_URL}/shop/customizations",
                        method="GET"
                    )
                    print("customizations_result:", customizations_result, "\n")

                    if "message" in customizations_result and len(customizations_result) == 2 and "no customizations" not in customizations_result["message"] and "An error occurred" not in customizations_result["message"]:
                        shouldRetry = True

                        if num_retries + 1 == max_retries:
                            customizations_message = json.dumps(customizations_result)
                    else: 
                        shouldRetry = False
                        customizations_result_code = customizations_result["code"]
                        customizations_message = json.dumps(customizations_result)

                    num_retries += 1

                # Reset
                shouldRetry = True
                num_retries = 0

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
                        customization["points"]
                    )

                possible_user_customizations_to_remove = []

                for customization in user_customizations_result_list:
                    customization_tuple = (
                        customization["customization_id"],
                        customizations_dict[customization["customization_id"]],
                    )
                    possible_user_customizations_to_remove.append(customization_tuple)

                to_remove_list = []

                while points_to_deduct_from_customizations > 0 and len(possible_user_customizations_to_remove) > 0:
                    points_to_deduct_from_customizations -= possible_user_customizations_to_remove[-1][1]
                    possible_user_customization_to_remove = possible_user_customizations_to_remove.pop()
                    to_remove_list.append(possible_user_customization_to_remove[0])
                
                final_points = abs(points_to_deduct_from_customizations)
                #change_points = user_points + points_to_deduct_from_customizations #must end up with this positive of this value


                # Delete user customizations
                customizations_to_delete = {
                    "user_id": user_id,
                    "to_remove_list": to_remove_list,
                }

                while num_retries < max_retries and delete_customizations_result_code not in range(200, 300) and shouldRetry == True:
                    print("-----Invoking user microservice-----")
                    delete_customizations_result = invoke_http(
                        f"{USER_MICROSERVICE_URL}/users/customization-purchase/delete",
                        method="DELETE",
                        json=customizations_to_delete,
                    )
                    print("delete_customizations_result:", delete_customizations_result, "\n")

                    if "message" in delete_customizations_result and len(delete_customizations_result) == 2 and "Customization purchase" not in delete_customizations_result["message"] and "Invalid JSON input" not in delete_customizations_result["message"]:
                        shouldRetry = True

                        if num_retries + 1 == max_retries:
                            delete_customizations_message = json.dumps(delete_customizations_result)
                    else: 
                        shouldRetry = False
                        delete_customizations_result_code = delete_customizations_result["code"]
                        delete_customizations_message = json.dumps(delete_customizations_result)

                    num_retries += 1

                # Reset
                shouldRetry = True
                num_retries = 0

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


                # Update user details
                selected_customization_id = user_details_result["data"]["selected_customization_id"]


                user_details_to_change = {}

                if selected_customization_id in to_remove_list:
                    user_details_to_change["selected_customization_id"] = None

                if (user_points - final_points) >= 0:
                    difference = user_points - final_points
                    user_details_to_change["points"] = difference / 100
                    user_details_to_change["operation"] = "subtract"
                
                else:
                    difference = final_points - user_points
                    user_details_to_change["points"] = difference / 100
                    user_details_to_change["operation"] = "add"

                while num_retries < max_retries and update_user_details_result_code not in range(200, 300) and shouldRetry == True:
                    print("-----Invoking user microservice-----")
                    update_user_details_result = invoke_http(
                        f"{USER_MICROSERVICE_URL}/users/" + str(user_id) + "/update",
                        method="PUT",
                        json=user_details_to_change,
                    )
                    print("update_user_details_result:", update_user_details_result, "\n")

                    if "message" in update_user_details_result and len(update_user_details_result) == 2 and "Invalid JSON input" not in update_user_details_result["message"]:
                        shouldRetry = True

                        if num_retries + 1 == max_retries:
                            update_user_details_message = json.dumps(update_user_details_result)
                    else: 
                        shouldRetry = False
                        update_user_details_result_code = update_user_details_result["code"]
                        update_user_details_message = json.dumps(update_user_details_result)

                    num_retries += 1

                # Reset
                shouldRetry = True
                num_retries = 0

                # error handle if cant retrieve
                if update_user_details_result_code not in range(200, 300):
                    print('\n\n-----Publishing the (user details update error) message with routing_key=user.details.update.error-----')

                    channel.basic_publish(exchange=exchangename, routing_key="user.details.update.error", 
                        body=update_user_details_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues 

                    # - reply from the invocation is not used;
                    # continue even if this invocation fails        
                    print("\nUser details update status ({:d}) published to the RabbitMQ Exchange:".format(
                        update_user_details_result_code), update_user_details_result)

                    result = {
                        "code": 500,
                        "data": {
                            "update_user_details_result": update_user_details_result
                        },
                        "message": "User details update error sent for error handling"
                    }

                    print('\n------------------------')
                    print('\nresult: ', result)
                    return jsonify(result), result["code"]

            # Delete purchase record
            del_json = {"user_id": user_id, "game_id": game_id}
            
            while num_retries < max_retries and delete_game_purchase_result_code not in range(200, 300) and shouldRetry == True:
                print("-----Invoking user microservice-----")
                delete_game_purchase_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/game-purchase/delete",
                    method="DELETE",
                    json=del_json,
                )
                print("delete_game_purchase_result:", delete_game_purchase_result, "\n")

                if "message" in delete_game_purchase_result and len(delete_game_purchase_result) == 2 and "Game purchase record" not in delete_game_purchase_result["message"] and "An error occurred" not in delete_game_purchase_result["message"] and "Invalid JSON input" not in delete_game_purchase_result["message"]:
                    shouldRetry = True

                    if num_retries + 1 == max_retries:
                        delete_game_purchase_message = json.dumps(delete_game_purchase_result)
                else: 
                    shouldRetry = False
                    delete_game_purchase_result_code = delete_game_purchase_result["code"]
                    delete_game_purchase_message = json.dumps(delete_game_purchase_result)

                num_retries += 1

            # Reset
            shouldRetry = True
            num_retries = 0

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

            while num_retries < max_retries and payment_refund_result_code not in range(200, 300) and shouldRetry == True:
                print('\n-----Invoking payment microservice-----')
                payment_refund_result = invoke_http(
                    f"{PAYMENT_MICROSERVICE_URL}/refund", method="POST", json=payment_refund_data
                )
                print('payment_refund_result:', payment_refund_result, '\n')

                if "message" in payment_refund_result and len(payment_refund_result) == 2 and "Refund failed" not in payment_refund_result["message"] and "An error occurred" not in payment_refund_result["message"] and "Invalid JSON input" not in payment_refund_result["message"]:
                    shouldRetry = True

                    if num_retries + 1 == max_retries:
                        payment_refund_message = json.dumps(payment_refund_result)
                else: 
                    shouldRetry = False
                    payment_refund_result_code = payment_refund_result["code"]
                    payment_refund_message = json.dumps(payment_refund_result)

                num_retries += 1

            # Reset
            shouldRetry = True
            num_retries = 0

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
                    "update_user_details_result": update_user_details_result,
                    "payment_refund_result": payment_refund_result
                }
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
