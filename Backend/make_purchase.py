from flask import Flask, request, jsonify
from flask_cors import CORS
import os, sys
from invokes import invoke_http
import pika
import json
import amqp_connection
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

# Initialize flasgger for API Documentation
app.config['SWAGGER'] = {
    'title': 'Make_Purchase Microservice API',
    'version': 2.0,
    "openapi": "3.0.2",
    'description': 'Orchestrate the process of making a .json is not shared from the host and is not known to Docker.purchase of a game.',
    'tags': {
        'Make_Purchase': 'Operations related to making a purchase of a game',
    },
}

swagger = Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF@34.124.211.169/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# AMQP connection setup
exchangename = "order_topic" # exchange name
exchangetype="topic" # use a 'topic' exchange to enable interaction
connection = amqp_connection.create_connection() 
channel = connection.channel()
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True) 
# If the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

#URLS
create_game_purchase_URL = "http://kong:8000/users/game-purchase/create"
game_details_URL = "http://kong:8000/shop/games/"
update_points_URL = "http://kong:8000/users/"
payment_URL = "http://kong:8000/payment"
update_game_purchase_URL = "http://kong:8000/users/game-purchase/update"
user_details_URL = "http://kong:8000/users/"
delete_game_purchase_URL = "http://kong:8000/users/game-purchase/delete"


@app.route("/make-purchase", methods=['POST'])
def make_purchase():
    """
    Makes a purchase for a game.
    ---
    tags:
      - Purchases
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            user_id:
              type: integer
              description: The ID of the user making the purchase.
            game_id:
              type: integer
              description: The ID of the game being purchased.
            purchase_id:
              type: string
              description: The ID of the purchase.
    responses:
      200:
        description: Purchase made successfully.
        schema:
          type: object
          properties:
            code:
              type: integer
              description: The HTTP status code.
            data:
              type: object
              description: The result of the purchase operation.
      400:
        description: Invalid JSON input.
        schema:
          type: object
          properties:
            code:
              type: integer
              description: The HTTP status code.
            message:
              type: string
              description: A message describing the error.
      500:
        description: Internal server error.
        schema:
          type: object
          properties:
            code:
              type: integer
              description: The HTTP status code.
            message:
              type: string
              description: A message describing the error.
    """
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            # get response body
            userid_gameid = request.get_json()
            user_id = userid_gameid['user_id']
            game_id = userid_gameid['game_id']

            # creates game purchase record
            create_game_purchase_result = create_game_purchase(userid_gameid)

            if(create_game_purchase_result['code'] in range(200, 300)):
                #get game details
                game_result = get_game_detail(game_id)

                if(game_result["code"] in range(200, 300)):
                    game_details = game_result["data"]["game_details_result"]["data"]
                    payment_json = json.dumps({
                        'price': game_details["price"],
                        'purchase_id': userid_gameid['purchase_id']
                    })
                    # payment
                    make_payment_result = make_payment(payment_json)["data"]["payment_result"]
                    if make_payment_result['code'] in range(200, 300):
                        # update game_purchase table
                        update_json = {
                            'user_id': user_id,
                            'game_id': game_id,
                            'transaction_id': make_payment_result['data']['id']
                        }
                        
                        update_game_purchase_result = update_game_purchase(update_json)
                        if update_game_purchase_result["code"] in range(200, 300):
                            # update points
                            update_points_result = update_points(user_id, game_details)

                            if update_points_result["code"] in range(200, 300):
                                user_details = update_points_result['data']["update_points_result"]["data"]
                                notification_json = {
                                    'game_price': game_details['price'],
                                    'game_title': game_details['title'],
                                    'email': user_details['email'],
                                    'account_name': user_details['account_name'],
                                    'purchase_id': make_payment_result['data']['id']
                                }    

                                print('processing notification...')
                                process_notification(notification_json)

                                result = {
                                    "code": 200,
                                    "data": {
                                        "make_payment_result": make_payment_result
                                    }
                                }

                                print('\n------------------------')
                                print('\nresult: ', result)

                                return jsonify(result), result["code"]
                            else:
                                print('\n------------------------')
                                print('\nresult: ', update_points_result)
                                return jsonify(update_points_result), update_points_result["code"]
                        else:
                            print('\n------------------------')
                            print('\nresult: ', update_game_purchase_result)
                            return jsonify(update_game_purchase_result), update_game_purchase_result["code"]
                    else:
                        rollback_record_result = rollback_record(user_id, game_id)

                        if rollback_record_result["code"] in range(200, 300):
                            user_details_result = get_user_details(user_id)

                            if user_details_result["code"] in range(200, 300):
                                user_details = user_details_result['data']["user_details_result"]["data"]
                                notification_json = {
                                    'game_price': game_details['price'],
                                    'game_title': game_details['title'],
                                    'email': user_details['email'],
                                    'account_name': user_details['account_name']
                                }    

                                print('processing notification...')
                                process_fail_notification(notification_json)

                                result = {
                                    "code": 500,
                                    "data": {
                                        "make_payment_result": make_payment_result
                                    },
                                    "message": make_payment_result["message"]
                                }

                                print('\n------------------------')
                                print('\nresult: ', result)

                                return jsonify(result), result["code"]
                            else:
                                print('\n------------------------')
                                print('\nresult: ', user_details_result)
                                return jsonify(user_details_result), user_details_result["code"]
                        else:
                            print('\n------------------------')
                            print('\nresult: ', rollback_record_result)
                            return jsonify(rollback_record_result), rollback_record_result["code"]
                else:
                    print('\n------------------------')
                    print('\nresult: ', rollback_record_result)
                    return jsonify(rollback_record_result), rollback_record_result["code"]
            else:
                print('\n------------------------')
                print('\nresult: ', game_result)
                return jsonify(game_result), game_result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify(
                {
                    "code": 500,
                    "message": "make_purchase.py internal error: " + ex_str
                }
            ), 500

    # if reached here, not a JSON request.
    return jsonify(
        {
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


def create_game_purchase(userid_gameid):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    create_game_purchase_result = {}
    create_game_purchase_result_code = 400
    create_game_purchase_message = ""

    # create entry in game_purchase table
    create_game_purchase_json = {
        "user_id": userid_gameid['user_id'],
        "game_id": userid_gameid['game_id']
    }

    while num_retries < max_retries and create_game_purchase_result_code not in range(200, 300) and shouldRetry == True:
        print('\n-----Invoking user microservice-----')
        create_game_purchase_result = invoke_http(create_game_purchase_URL, method='POST', json=create_game_purchase_json)
        print('create_game_purchase_result:', create_game_purchase_result, '\n')

        if "message" in create_game_purchase_result and len(create_game_purchase_result) == 2 and "Invalid JSON input" not in create_game_purchase_result["message"] and "An error occurred" not in create_game_purchase_result["message"]:
            shouldRetry = True

            if num_retries + 1 == max_retries:
                create_game_purchase_message = json.dumps(create_game_purchase_result)
        else: 
            shouldRetry = False
            create_game_purchase_result_code = create_game_purchase_result["code"]
            create_game_purchase_message = json.dumps(create_game_purchase_result)

        num_retries += 1

    # Reset
    shouldRetry = True
    num_retries = 0
 
    if create_game_purchase_result_code not in range(200, 300):
        print('\n\n-----Publishing the (game purchase creation error) message with routing_key=game.purchase.creation.error-----')

        # print('---------message')
        # print(create_game_purchase_message)
        # print('-----------end message')

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
    
    return {
        "code": 201,
        "data": {
            "create_game_purchase_result": create_game_purchase_result            
        }
    }

def get_game_detail(game_id):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    game_details_result = {}
    game_details_result_code = 400
    game_details_message = ""

    # get game details
    while num_retries < max_retries and game_details_result_code not in range(200, 300) and shouldRetry == True:
        print('\n-----Invoking shop microservice-----')
        game_details_result = invoke_http(game_details_URL + str(game_id), method='GET')
        print('game_details_result:', game_details_result, '\n')

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
        print('\n\n-----Publishing the (game details error) message with routing_key=game.details.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="game.details.error", 
            body=game_details_message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nGame details status ({:d}) published to the RabbitMQ Exchange:".format(
            game_details_result_code), game_details_result)

        # Return error
        return {
            "code": 500,
            "data": { 
                "game_details_result": game_details_result 
            },
            "message": "Game details error sent for error handling"
        }
    return {
        "code": 201,
        "data": {
            "game_details_result": game_details_result
        }
    }
def make_payment(payment_json):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    payment_result = {}
    payment_result_code = 400
    payment_message = ""

    while num_retries < max_retries and (payment_result_code not in range(200, 300) or shouldRetry == True):
        print('\n-----Invoking payment microservice-----')
        payment_result = invoke_http(payment_URL, method='POST', json=payment_json)
        print("payment_result: ", payment_result, '\n')

        #returns client secret and id

        if "message" in payment_result and len(payment_result) == 2 and "Invalid JSON input" not in payment_result["message"] and "An error occurred" not in payment_result["message"]:
            shouldRetry = True

            if num_retries + 1 == max_retries:
                payment_message = json.dumps(payment_result)
        else: 
            shouldRetry = False
            payment_result_code = payment_result["code"]
            payment_message = json.dumps(payment_result)

        num_retries += 1

    # Reset
    shouldRetry = True
    num_retries = 0

    if payment_result_code not in range(200, 300):
        print('\n\n-----Publishing the (payment error) message with routing_key=payment.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="payment.error", 
            body=payment_message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nPayment status ({:d}) published to the RabbitMQ Exchange:".format(
            payment_result_code), payment_result)

        # Return error
        return {
            "code": 500,
            "data": {
                "payment_result": payment_result
            },
            "message": "Payment error sent for error handling"
        }

    return {
        "code": 200,
        "data": {
            "payment_result": payment_result
        }
    }


def update_game_purchase(update_json):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    update_game_purchase_result = {}
    update_game_purchase_result_code = 400
    update_game_purchase_message = ""

    while num_retries < max_retries and update_game_purchase_result_code not in range(200, 300) and shouldRetry == True:
        print('\n-----Invoking user microservice-----')
        update_game_purchase_result = invoke_http(update_game_purchase_URL, method='PUT', json=update_json)
        print('update_game_purchase_result:', update_game_purchase_result, '\n')

        if "message" in update_game_purchase_result and len(update_game_purchase_result) == 2 and "Invalid JSON input" not in update_game_purchase_result["message"] and "An error occurred" not in update_game_purchase_result["message"]:
            shouldRetry = True

            if num_retries + 1 == max_retries:
                update_game_purchase_message = json.dumps(update_game_purchase_result)
        else: 
            shouldRetry = False
            update_game_purchase_result_code = update_game_purchase_result["code"]
            update_game_purchase_message = json.dumps(update_game_purchase_result)

        num_retries += 1

    # Reset
    shouldRetry = True
    num_retries = 0

    if update_game_purchase_result_code not in range(200, 300):
        print('\n\n-----Publishing the (game purchase update error) message with routing_key=game.purchase.update.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="game.purchase.update.error", 
            body=update_game_purchase_message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nGame purchase update status ({:d}) published to the RabbitMQ Exchange:".format(
            update_game_purchase_result_code), update_game_purchase_result)

        # Return error
        return {
            "code": 500,
            "data": {
                "update_game_purchase_result": update_game_purchase_result
            },
            "message": "Game purchase update error sent for error handling"
        }
    
    return {
        "code": 200,
        "data": {
            "update_game_purchase_result": update_game_purchase_result
        }
    }


def update_points(user_id, game_details):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    update_points_result = {}
    update_points_result_code = 400
    update_points_message = ""

    points_json = {
        "points": game_details["price"],
        "operation": "add"
    }

    while num_retries < max_retries and update_points_result_code not in range(200, 300) and shouldRetry == True:
        print('\n-----Invoking user microservice-----')
        update_points_result = invoke_http(update_points_URL + str(user_id) + "/update", method='PUT', json=points_json)
        print("update_points_result: ", update_points_result, '\n')

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

        # Return error
        return {
            "code": 500,
            "data": {
                "update_points_result": update_points_result
            },
            "message": "Points update error sent for error handling"
        }

    return {
        "code": 200, 
        "data": {
            "update_points_result": update_points_result
        }
    }


def get_user_details(user_id):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    user_details_result = {}
    user_details_result_code = 400
    user_details_message = ""

    while num_retries < max_retries and user_details_result_code not in range(200, 300) and shouldRetry == True:
        print('\n-----Invoking user microservice-----')
        user_details_result = invoke_http(user_details_URL + str(user_id), method='GET')
        print('user_details_result:', user_details_result, '\n')

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

        # Return error
        return {
            "code": 500,
            "data": {
                "user_details_result": user_details_result
            },
            "message": "User details error sent for error handling"
        }
    
    return {
        "code": 200,
        "data": {
            "user_details_result": user_details_result
        }
    }


def process_notification(notification_json):
    message = notification_json

    print('\n\n-----Publishing the notification with routing_key=purchase.notification-----')

    # try:
    channel.basic_publish(exchange=exchangename, routing_key="purchase.notification", 
        body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
        # print("published")
    # make message persistent within the matching queues 

    # - reply from the invocation is not used;
    # continue even if this invocation fails        
    # except Exception as e:
    #     # Unexpected error in code
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
    #     print(ex_str)
 
def process_fail_notification(notification_json):
    message = notification_json

    print('\n\n-----Publishing the notification with routing_key=fail.notification-----')

    # try:
    channel.basic_publish(exchange=exchangename, routing_key="fail.notification", 
        body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
        # print("published")
    # make message persistent within the matching queues 

    # - reply from the invocation is not used;
    # continue even if this invocation fails        
    # except Exception as e:
    #     # Unexpected error in code
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #     ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
    #     print(ex_str)
        
def rollback_record(user_id, game_id):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    delete_game_purchase_result = {}
    delete_game_purchase_result_code = 400
    delete_game_purchase_message = ""

    delete_game_purchase_json = {
        "user_id": user_id,
        "game_id": game_id
    }

    while num_retries < max_retries and delete_game_purchase_result_code not in range(200, 300) and shouldRetry == True:
        print('\n-----Invoking user microservice-----')
        delete_game_purchase_result = invoke_http(delete_game_purchase_URL, method='DELETE', json=delete_game_purchase_json)
        print('delete_game_purchase_result:', delete_game_purchase_result, '\n')

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

    if delete_game_purchase_result_code not in range(200, 300):
        print('\n\n-----Publishing the (game purchase deletion error) message with routing_key=game.purchase.deletion.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="game.purchase.deletion.error", 
            body=delete_game_purchase_message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nGame purchase deletion status ({:d}) published to the RabbitMQ Exchange:".format(
            delete_game_purchase_result_code), delete_game_purchase_result)

        # Return error
        return {
            "code": 500,
            "data": { 
                "delete_game_purchase_result": delete_game_purchase_result 
            },
            "message": "Game purchase deletion error sent for error handling"
        }
    
    return {
        "code": 200,
        "data": {
            "delete_game_purchase_result": delete_game_purchase_result
        }
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5605, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
