from flask import Flask, request, jsonify
from invokes import invoke_http
from flask_cors import CORS
import requests
import pika
import amqp_connection
import os, sys
import json

app = Flask(__name__)
CORS(app)

# Define the microservices URLs
USER_MICROSERVICE_URL = "http://localhost:5101"
PAYMENT_MICROSERVICE_URL = "http://localhost:5666"
ERROR_MICROSERVICE_URL = "http://localhost:5445/error"
SHOP_CUSTOMIZATION_MICROSERVICE_URL = "http://localhost:5000"

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


# def log_error(user_id, error_message):
#     # Function to log errors to the Error Microservice.
#     error_data = {"user_id": user_id, "error_message": error_message}
#     print("-----Invoking error microservice-----")
#     invoke_http(f"{ERROR_MICROSERVICE_URL}/log", method="POST", json=error_data)


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
        print("published")
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


@app.route("/refund", methods=["POST"])
def process_refund():
    # Pull data first
    print(request.get_json())
    if request.is_json:
        try:
            data = request.get_json()
            print(data)
            user_id = data["user_id"]
            game_id = data["game_id"]
            print("-----Invoking shop microservice-----")
            gamedetail = invoke_http(
                f"{SHOP_CUSTOMIZATION_MICROSERVICE_URL}/games/{game_id}", method="GET"
            )
            print("game_detail_result:", gamedetail, "\n")
            gamedetail_message = json.dumps(gamedetail)

            if gamedetail["code"] not in range(200, 300):
                print(
                    "\n\n-----Publishing the (game details error) message with routing_key=game.details.error-----"
                )

                channel.basic_publish(
                    exchange=exchangename,
                    routing_key="game.details.error",
                    body=gamedetail_message,
                    properties=pika.BasicProperties(delivery_mode=2),
                )
                # make message persistent within the matching queues

                # - reply from the invocation is not used;
                # continue even if this invocation fails
                print(
                    "\nGame details status ({:d}) published to the RabbitMQ Exchange:".format(
                        gamedetail["code"]
                    ),
                    gamedetail,
                )

                # Return error
                return {
                    "code": 500,
                    "data": {"game_details_result": gamedetail},
                    "message": "Game details error sent for error handling",
                }

            points_to_deduct = gamedetail["data"]["points"]
            print("points to deduct:")
            print(points_to_deduct)

            # Step 1: Retrieve user's gameplay time and purchase id
            print("-----Invoking user microservice-----")
            create_game_purchase_result = invoke_http(
                f"{USER_MICROSERVICE_URL}/game-purchase/{user_id}/{game_id}",
                method="GET",
            )
            print(create_game_purchase_result)

            create_game_purchase_result_code = create_game_purchase_result["code"]
            create_game_purchase_message = json.dumps(create_game_purchase_result)
 
            if create_game_purchase_result_code not in range(200, 300):
                print('\n\n-----Publishing the (game purchase creation error) message with routing_key=game.purchase.creation.error-----')

                channel.basic_publish(exchange=exchangename, routing_key="game.purchase.creation.error", 
                    body=create_game_purchase_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                # make message persistent within the matching queues 

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nGame purchase creation status ({:d}) published to the RabbitMQ Exchange:".format(
                    create_game_purchase_result_code), create_game_purchase_result)

                # Return error
                return {
                    "code": 500,
                    "data": {
                        "create_game_purchase_result": create_game_purchase_result
                    },
                    "message": "Game purchase creation error sent for error handling"
                }

            gameplay_time = create_game_purchase_result["data"]["gameplay_time"]
            purchase_id = create_game_purchase_result["data"]["payment_intent"]
            print(2)
            print("gameplay time:")
            print(gameplay_time)

            # Step 2: Check for refund eligibility
            if gameplay_time and gameplay_time >= 120:
                print("gameplay more than 2 hours")
                return (
                    jsonify({"error": "Refund ineligible due to gameplay time."}),
                    400,
                )
            
            #change to AMQP

            # Step 3: Get user points
            print("-----Invoking user microservice-----")
            user_details_result = invoke_http(
                f"{USER_MICROSERVICE_URL}/users/{user_id}", method="GET"
            )
            print(user_details_result)

            user_details_result_code = user_details_result['code']
            user_details_message = json.dumps(user_details_result)
            # print(message)

            if user_details_result_code not in range(200, 300):
                print('\n\n-----Publishing the (user details error) message with routing_key=user.details.error-----')

                channel.basic_publish(exchange=exchangename, routing_key="user.details.error", 
                    body=user_details_message, properties=pika.BasicProperties(delivery_mode = 2)) 
                # make message persistent within the matching queues 

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nUser details status ({:d}) published to the RabbitMQ Exchange:".format(
                    user_details_result_code), user_details_result)

                # Return error
                return {
                    "code": 500,
                    "data": {
                        "user_details_result": user_details_result
                    },
                    "message": "User details error sent for error handling"
                }
        
            user_points = user_details_result["data"]["points"]
            print("user points:")
            print(user_points)

            # Step 4: Check if points are sufficient

            if user_points >= points_to_deduct:
                # invoke user.py endpoint that only updates the points
                points_to_change = {"operation": "-", "price": points_to_deduct / 100}
                print("-----Invoking user microservice-----")
                update_points_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/{user_id}/points/update",
                    method="PUT",
                    json=points_to_change,
                )
                print(update_points_result)
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

                    # Return error
                    return {
                        "code": 500,
                        "data": {
                            "update_points_result": update_points_result
                        },
                        "message": "Points update error sent for error handling"
                    }
                if update_points_result["code"] != 200:
                    #log_error(user_id, "Failed to update user points")
                    return jsonify({"error": "Failed to update user points."}), 500
            else:
                remaining = points_to_deduct - user_points
                print("remaining points to deduct:")
                print(remaining)

                user_item_purchase_history = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/{user_id}/customizations",
                    method="GET",
                )
                print(user_item_purchase_history)
                # error handle if cant retrieve
                if user_item_purchase_history["code"] not in range(200, 300):
                    #log_error(user_id, "Failed to retrieve user item purchase history")
                    return (
                        jsonify(
                            {"error": "Failed to retrieve user item purchase history."}
                        ),
                        500,
                    )

                user_item_purchase_history_list = user_item_purchase_history["data"]
                print("items user owns:")
                print(user_item_purchase_history_list)
                customizations = invoke_http(
                    f"{SHOP_CUSTOMIZATION_MICROSERVICE_URL}/customizations",
                    method="GET",
                )
                if customizations["code"] not in range(200, 300):
                    #log_error(user_id, "Failed to retrieve customizations")
                    return jsonify({"error": "Failed to retrieve customizations."}), 500

                customizations_list = customizations["data"]["customizations"]
                customizations_dict = {}
                for customization in customizations_list:
                    customizations_dict[customization["customization_id"]] = (
                        customization["credits"]
                    )
                print("custom dict:")
                print(customizations_dict)

                list_to_run = []
                for item in user_item_purchase_history_list:
                    item_tuple = (
                        item["customization_id"],
                        customizations_dict[item["customization_id"]],
                    )
                    list_to_run.append(item_tuple)
                print("all of user items:")
                print(list_to_run)

                to_remove_list = []

                print(list_to_run[-1][1])
                while (remaining > 0) and (len(list_to_run) > 0):
                    print("remaining:")
                    print(remaining)
                    print("last item pointa")
                    print(list_to_run[-1][1])
                    remaining -= list_to_run[-1][1]
                    last_customization = list_to_run.pop()
                    to_remove_list.append(last_customization[0])
                    print(to_remove_list)
                print("items to remove:")
                print(to_remove_list)

                change_points = user_points + remaining
                print("points to deduct")
                print(change_points)
                operation = "minus"

                customizations_to_delete = {
                    "user_id": user_id,
                    "to_remove_list": to_remove_list,
                }
                delete_customizations = invoke_http(
                    f"{USER_MICROSERVICE_URL}/customizations/delete",
                    method="DELETE",
                    json=customizations_to_delete,
                )
                print(delete_customizations)
                if delete_customizations["code"] not in range(200, 300):
                    #log_error(user_id, "Failed to delete customizations")
                    return jsonify({"error": "Failed to delete customizations."}), 500
                print("items deleted successfully")
                points_to_change = {
                    "operation": operation,
                    "price": abs(change_points / 100),
                }
                update_points_result = invoke_http(
                    f"{USER_MICROSERVICE_URL}/users/{user_id}/points/update",
                    method="PUT",
                    json=points_to_change,
                )
                print(update_points_result)
                if update_points_result["code"] not in range(200, 300):
                    #log_error(
                    #    user_id, "Failed to update points after deleting customizations"
                    #)
                    return (
                        jsonify(
                            {
                                "error": "Failed to update points after deleting customizations."
                            }
                        ),
                        500,
                    )
                print("points deducted successfully")
                print("success")

            # Step 5: Delete purchase record
            del_json = {"user_id": user_id, "game_id": game_id}
            delete_purchase_record = invoke_http(
                f"{USER_MICROSERVICE_URL}/game-purchase/delete",
                method="DELETE",
                json=del_json,
            )
            print(delete_purchase_record)
            if delete_purchase_record["code"] != 200:
                return jsonify({"error": "Failed to delete purchase record."}), 500
            # the error handling above cannot uncomment. If i uncomment, it doesnt run to the next part

            # Step 6: Process the refund through Stripe
            payment_intent_id = purchase_id
            refund_data = {"payment_intent": payment_intent_id}
            payment_response = invoke_http(
                f"{PAYMENT_MICROSERVICE_URL}/refund", method="POST", json=refund_data
            )
            print(payment_response)
            print("done!")
            if payment_response["code"] != 200:
                return (
                    jsonify({"error": "Failed to process refund through Stripe."}),
                    500,
                )
            print("processing notif")

            # Step 7: Send email notification to user

            notification_json = {
                "game_price": gamedetail["data"]["price"],
                "game_title": gamedetail["data"]["title"],
                "email": user_response["data"]["email"],
                "account_name": user_response["data"]["account_name"],
                "purchase_id": payment_intent_id,
            }
            print(notification_json)

            print("processing notification...")
            process_refund_notification(notification_json)

            # If everything is successful, return confirmation
            return jsonify({"message": "Refund processed successfully."}), 200
        except:
            return {"code": "400"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200, debug=True)
