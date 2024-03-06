from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http
import pika
import json
import amqp_connection

app = Flask(__name__)
CORS(app)
exchangename = "make_purchase_topic" # exchange name
exchangetype="topic" # use a 'topic' exchange to enable interaction
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

payment_URL = "http://localhost:5000/create-checkout-session"
notification_URL = "http://localhost:5000/notification"
user_purchase_URL = "http://localhost:5000/game-purchase"
user_point_URL = "http://localhost:5000/points/update"
error_URL = "http://localhost:5000/error"


@app.route("/make_purchase", methods=['POST'])
def make_purchase():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            purchase = request.get_json()
            updateuser = create_purchase(purchase)
            result = process_purchase(purchase)
            #sends notification message to AMQP queue
            channel.basic_publish(exchange=exchangename, routing_key="notification.info", 
                body=message)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def create_purchase(purchase):
    #create entry in purchase_game table
    #modifies purchase json into wtv u need for below function
    purchase1 = jsonify()
    create_purchase_result = invoke_http(user_purchase_URL, method='POST', json=purchase1)
    code = create_purchase_result["code"]
    message = json.dumps(create_purchase_result)

 
    if code not in range(200, 300):
        print('\n\n-----Publishing the (create error) message with routing_key=create.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="create.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), create_purchase_result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"create_result": create_purchase_result},
            "message": "Purchase creation failure sent for error handling."
        }



    #update user points
    #purchse 2 should have userid and update amt
    purchase2 = jsonify()
    update_points_result = invoke_http(user_point_URL, method='POST', json=purchase2)
    code = update_points_result["code"]
    message = json.dumps(update_points_result)

 
    if code not in range(200, 300):
        print('\n\n-----Publishing the (point error) message with routing_key=point.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="point.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), update_points_result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"update_points_result": update_points_result},
            "message": "Points update failure sent for error handling."
        }

    data = {"code": 200, "data": {"result": "success"}}
    return data


def process_purchase(purchase):
    
    # Invoke the notification microservice
    print('\n-----Invoking order microservice-----')
    purchase_result = invoke_http(payment_URL, method='POST', json=purchase)
    # Check the purchase result; if a failure, send it to the error microservice.
    code = purchase_result["code"]
    message = json.dumps(purchase_result)

 
    if code not in range(200, 300):
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="payment.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), purchase_result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"order_result": purchase_result},
            "message": "Order creation failure sent for error handling."
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
