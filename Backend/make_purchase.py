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
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
CORS(app)


#AMQP STUFF
exchangename = "order_topic" # exchange name
exchangetype="topic" # use a 'topic' exchange to enable interaction
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

#URLS
payment_URL = "http://localhost:5666/payment"
notification_URL = "http://localhost:5200/notification"
user_purchase_URL = "http://localhost:5101/game-purchase"
user_point_URL = "http://localhost:5600/points/add"
error_URL = "http://localhost:5100/error"
userdetails_URL = "http://localhost:5101/userdetail/"
gamedetails_URL = "http://localhost:5000/gamedetail/"
update_purchase_table_URL = "http://localhost:5101/update-game-purchase"


#USER TABLE
class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    account_name = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    points = db.Column(db.Float)

    def __init__(self, user_id, email, account_name, password, points):
        self.user_id = user_id
        self.email = email
        self.account_name = account_name
        self.password = password
        self.points = points

    def json(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "account_name": self.account_name,
            "password": self.password,
            "points": self.points
        }
# @app.before_request
# def handle_options():
#     if request.method == 'OPTIONS':
#         response = Response()
#         response.headers['Access-Control-Allow-Origin'] = '*'
#         response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
#         response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
#         response.headers['Content-Type'] = 'application/json'
#         return response
    
@app.route("/payment-fail", methods=['POST'])

# @cross_origin()
# def rollback():


@app.route("/make-purchase", methods=['POST'])

# @cross_origin()
def make_purchase():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            #get response body

            userid_gameid = request.get_json()
            print(userid_gameid)
            user_id = userid_gameid['user_id']
            game_id = userid_gameid['game_id']

            
            


            #updates gamepurchase table and updates points
            updateuser = create_purchase(userid_gameid)
            if(updateuser['code'] == 202):
                gamedetailsjson = invoke_http(gamedetails_URL + str(userid_gameid['game_id']), method='GET')
                gamedetails = gamedetailsjson['data']
                print("printing price")
                price = gamedetails['price']
                print(price)


                
                payment_json = json.dumps({
                                'price': gamedetails['price'],
                                'paymentmethod_id': userid_gameid['paymentmethod_id']
                })
                #payment
                payment_result = make_payment(payment_json)
                print('payment done')
                if payment_result['code'] in range(200, 300):
                    print('payment successful')
                    #update gamepurchase table
                    updatejson = {'user_id': user_id,
                                  'game_id': game_id,
                                  'transaction_id': payment_result['confirmation']['id']

                    }
                    print(updatejson)
                    update_result = update_purchase_table(updatejson)
                    userdetailsjson = invoke_http(userdetails_URL + str(user_id), method='GET')
                    userdetails = userdetailsjson['data']
                    notification_json = {
                    
                        'price': gamedetails['price'],
                        'title': gamedetails['title'],
                        'email': userdetails['email'],
                        'account_name': userdetails['account_name'],
                        'transactionid': payment_result['confirmation']['id']

                    }
                    print('processing notification...')
                    process_notification(notification_json)
    
                else:
                    return
                    #rollback function TBD
        
                
            #NEED TO RETURN 
            return jsonify({
                
                "sucess": "succes!",
                "code": 200

            }), 202

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

def update_purchase_table(updatejson):
    update_purchase = invoke_http(update_purchase_table_URL, method='PUT', json=updatejson)
    code = update_purchase['code']
    message = json.dumps(update_purchase)
    print(message)
    if code not in range(200, 300):
        print('\n\n-----Publishing the (update error) message with routing_key=update_purchase.error-----')

        channel.basic_publish(exchange=exchangename, routing_key="update_purchase.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        # make message persistent within the matching queues 

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), update_purchase)

        # 7. Return error
        return {
            "code": 500,
            "data": {"create_result": update_purchase},
            "message": "Update failure sent for error handling."
        }




def create_purchase(userid_gameid):
    #create entry in purchase_game table
    print(userid_gameid)
    createjson = {"user_id": userid_gameid['user_id'],
                  "game_id": userid_gameid['game_id']
    }
    create_purchase_result = invoke_http(user_purchase_URL, method='POST', json=createjson)
    print(create_purchase_result)
    code = create_purchase_result["code"]
    message = json.dumps(create_purchase_result)
    print(message)


 
    if code not in range(200, 300):
        print('\n\n-----Publishing the (create error) message with routing_key=create_purchase.error-----')

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



    # update user points
    # purchse 2 should have userid and update amt
    gamedetailsjson = invoke_http(gamedetails_URL + str(userid_gameid['game_id']), method='GET')
    gamedetails = gamedetailsjson['data']
    print(gamedetails)
    pointsjson = {
        "user_id": userid_gameid['user_id'],
        "price": gamedetails['price']
    }
    print(pointsjson)
    print(json.dumps(pointsjson))
   
    update_points_result = invoke_http(user_point_URL, method='POST', json=pointsjson)
    code = update_points_result["code"]
    message = json.dumps(update_points_result)

 
    if code not in range(200, 300):
        print('\n\n-----Publishing the (point error) message with routing_key=point.error-----')

        # channel.basic_publish(exchange=exchangename, routing_key="point.error", 
        #     body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
    #     # make message persistent within the matching queues 

    #     # - reply from the invocation is not used;
    #     # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
            code), update_points_result)

    #     # 7. Return error
        return {
            "code": 500,
            "data": {"update_points_result": update_points_result},
            "message": "Points update failure sent for error handling."
        }

    data = {"code": 202, "data": {"result": "success"}}
    return data

def make_payment(payment_json):
    payment_result = invoke_http(payment_URL, method='POST', json=payment_json)
    
    print(payment_result)

    #returns client secret and id

    return payment_result


def process_notification(notification_json):
    
    # message = {
    #     "email": "zexter18518@gmail.com",
    #     "name": "zexter",
    #     "gamename": "eldenring",
    #     "price": 20,
    #     "transactionid": "osopfof_1231"
         
    # }
    message = notification_json

    print('\n\n-----Publishing the notification with routing_key=purchase.notification-----')

    try:
        channel.basic_publish(exchange=exchangename, routing_key="purchase.notification", 
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
