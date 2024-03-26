from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import os, sys
from invokes import invoke_http
import pika
import json
import amqp_connection
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF@34.124.211.169/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)


# AMQP STUFF
def create_notification_queue(channel):
    print('amqp_setup:create_notification_queue')
    a_queue_name = 'Notification_Log'
    channel.queue_declare(queue=a_queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchangename, queue=a_queue_name, routing_key='purchase.notification')
        # bind the queue to the exchange via the key
        # 'routing_key=#' => any routing_key would be matched
    
def create_notification_queue_2(channel):
    print('amqp_setup:create_notification_queue_2')
    a_queue_name = 'Notification_Log_Fail'
    channel.queue_declare(queue=a_queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    channel.queue_bind(exchange=exchangename, queue=a_queue_name, routing_key='fail.notification')
        # bind the queue to the exchange via the key
        # 'routing_key=#' => any routing_key would be matched
    
# function to create Error queue
def create_error_queue(channel):
    print('amqp_setup:create_error_queue')
    e_queue_name = 'Error'
    channel.queue_declare(queue=e_queue_name, durable=True) # 'durable' makes the queue survive broker restarts
    #bind Error queue
    channel.queue_bind(exchange=exchangename, queue=e_queue_name, routing_key='*.error')
        # bind the queue to the exchange via the key
        # any routing_key with two words and ending with '.error' will be matched
exchangename = "order_topic" # exchange name
exchangetype="topic" # use a 'topic' exchange to enable interaction
connection = amqp_connection.create_connection() 
channel = connection.channel()
channel.exchange_declare(exchange=exchangename, exchange_type=exchangetype, durable=True) 
print('amqp_setup:create queues')
create_error_queue(channel)
create_notification_queue(channel)
create_notification_queue_2(channel)

# if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

#URLS
create_game_purchase_URL = "http://localhost:5101/game-purchase/create"
game_details_URL = "http://localhost:5000/games/"
update_points_URL = "http://localhost:5101/users/"
payment_URL = "http://localhost:5666/payment"
update_game_purchase_URL = "http://localhost:5101/game-purchase/update"
user_details_URL = "http://localhost:5101/users/"
delete_game_purchase_URL = "http://localhost:5101/game-purchase/delete"
notification_URL = "http://localhost:5200/notification"
error_URL = "http://localhost:5100/error"
# user_point_URL = "http://localhost:5600/points/add"


@app.route("/make-purchase", methods=['POST'])
def make_purchase():
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
                # gamessjson = invoke_http(game_details_URL + str(userid_gameid['game_id']), method='GET')
                # gamess = gamessjson['data']
                # print("printing price")
                # price = gamess['price']
                # print(price)                

                # payment
                game_details = create_game_purchase_result["data"]["game_details_result"]["data"]
                payment_json = json.dumps({
                    'price': game_details["price"],
                    'purchase_id': userid_gameid['purchase_id']
                })

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
                        # # get user details
                        # user_details_result = get_user_details(user_id)

                        # update points
                        update_points_result = update_points(user_id, game_details)

                        if update_points_result["code"] in range(200, 300):
                            # userdetailsjson = invoke_http(user_details_URL + str(user_id), method='GET')
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

                            print('\n------------------------')
                            print('\nresult: ', update_game_purchase_result)

                            return jsonify(
                                {
                                    "code": 200,
                                    "data": update_game_purchase_result
                                }
                            ), 200
                        else:
                            return jsonify(update_points_result), update_points_result["code"]
                    else:
                        return jsonify(update_game_purchase_result), update_game_purchase_result["code"]
                else:
                    #rollback function TBD
                    # try:
                        # point_result = rollback_points(game_details)
                        rollback_record_result = rollback_record(user_id, game_id)

                        if rollback_record_result["code"] in range(200, 300):
                            # userdetailsjson = invoke_http(user_details_URL + str(user_id), method='GET')
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

                                # remove password key
                                # print("here: ", user_details_result)
                                del user_details_result['data']["user_details_result"]["data"]['password']

                                return jsonify(
                                    {
                                        "code": 500,
                                        "data": {
                                            "user_details_result": user_details_result
                                        },
                                        "message": make_payment_result["message"]
                                    }
                                ), 500
                            else:
                                return jsonify(user_details_result), user_details_result["code"]
                        else:
                            return jsonify(rollback_record_result), rollback_record_result["code"]
                    
                    # except Exception as e:
                    #     # Unexpected error in code
                    #     exc_type, exc_obj, exc_tb = sys.exc_info()
                    #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    #     ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
                    #     print(ex_str)

                    # return {'code': 200, 'data': {'result': 'rollback success'}}
            else:
                return jsonify(create_game_purchase_result), create_game_purchase_result["code"]

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
    # create entry in game_purchase table
    create_game_purchase_json = {
        "user_id": userid_gameid['user_id'],
        "game_id": userid_gameid['game_id']
    }

    print('\n-----Invoking user microservice-----')
    create_game_purchase_result = invoke_http(create_game_purchase_URL, method='POST', json=create_game_purchase_json)
    print('create_game_purchase_result:', create_game_purchase_result, '\n')

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
    
    # get game details
    print('\n-----Invoking shop microservice-----')
    game_details_result = invoke_http(game_details_URL + str(userid_gameid['game_id']), method='GET')
    print('game_details_result:', game_details_result, '\n')

    game_details_result_code = game_details_result["code"]
    game_details_message = json.dumps(game_details_result)

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
            "create_game_purchase_result": create_game_purchase_result,
            "game_details_result": game_details_result
        }
    }

    # game = game_details_result['data']
    # points_json = {
    #     # "user_id": userid_gameid['user_id'],
    #     "price": game['price'],
    #     "operation": "add"
    # }
    # # print(pointsjson)
    # # print(json.dumps(pointsjson))
   
    # print('\n-----Invoking user microservice-----')
    # update_points_result = invoke_http(update_points_URL + str(userid_gameid['user_id']) + "/points/update", method='PUT', json=points_json)
    # print("update_points_result: ", update_points_result, '\n')

    # update_points_result_code = update_points_result["code"]
    # update_points_message = json.dumps(update_points_result)

    # if update_points_result_code not in range(200, 300):
    #     print('\n\n-----Publishing the (points error) message with routing_key=points.error-----')

    #     channel.basic_publish(exchange=exchangename, routing_key="points.error", 
    #         body=update_points_message, properties=pika.BasicProperties(delivery_mode = 2)) 
    #     # make message persistent within the matching queues 

    #     # - reply from the invocation is not used;
    #     # continue even if this invocation fails        
    #     print("\nPoints update status ({:d}) published to the RabbitMQ Exchange:".format(
    #         update_points_result_code), update_points_result)

    #     # Return error
    #     return {
    #         "code": 500,
    #         "data": {
    #             "update_points_result": update_points_result
    #         },
    #         "message": "Points update error sent for error handling"
    #     }

    # data = {
    #     "code": 202, 
    #     "data": {
    #         "game_details_result": game_details_result
    #     }}
    # return data


def make_payment(payment_json):
    print('\n-----Invoking payment microservice-----')
    payment_result = invoke_http(payment_URL, method='POST', json=payment_json)
    print("payment_result: ", payment_result, '\n')

    #returns client secret and id

    payment_result_code = payment_result["code"]
    payment_message = json.dumps(payment_result)

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
    print('\n-----Invoking user microservice-----')
    update_game_purchase_result = invoke_http(update_game_purchase_URL, method='PUT', json=update_json)
    print('update_game_purchase_result:', update_game_purchase_result, '\n')

    update_game_purchase_result_code = update_game_purchase_result['code']
    update_game_purchase_message = json.dumps(update_game_purchase_result)

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
        }, 500
    
    return {
        "code": 200,
        "data": {
            "update_game_purchase_result": update_game_purchase_result
        }
    }


def update_points(user_id, game_details):
    # gamessjson = invoke_http(game_details_URL + str(userid_gameid['game_id']), method='GET')
    # gamess = gamessjson['data']
    points_json = {
        # "user_id": user_id,
        "price": game_details["price"],
        "operation": "add"
    }

    print('\n-----Invoking user microservice-----')
    update_points_result = invoke_http(update_points_URL + str(user_id) + "/points/update", method='PUT', json=points_json)
    print("update_points_result: ", update_points_result, '\n')

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

    return {
        "code": 200, 
        "data": {
            "update_points_result": update_points_result
        }
    }


def get_user_details(user_id):
    print('\n-----Invoking user microservice-----')
    user_details_result = invoke_http(user_details_URL + str(user_id), method='GET')
    print('user_details_result:', user_details_result, '\n')

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

    try:
        channel.basic_publish(exchange=exchangename, routing_key="fail.notification", 
            body=json.dumps(message), properties=pika.BasicProperties(delivery_mode = 2)) 
        print("published")
    # make message persistent within the matching queues 

    # - reply from the invocation is not used;
    # continue even if this invocation fails        
    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        
def rollback_record(user_id, game_id):
    delete_game_purchase_json = {
        "user_id": user_id,
        "game_id": game_id
    }

    print('\n-----Invoking user microservice-----')
    delete_game_purchase_result = invoke_http(delete_game_purchase_URL, method='DELETE', json=delete_game_purchase_json)
    print('delete_game_purchase_result:', delete_game_purchase_result, '\n')

    delete_game_purchase_result_code = delete_game_purchase_result["code"]
    delete_game_purchase_message = json.dumps(delete_game_purchase_result)

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
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
