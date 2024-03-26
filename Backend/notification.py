from mailjet_rest import Client
from flask import Flask, redirect, request
import amqp_connection
import json
import pika
from flask_cors import CORS

app = Flask(__name__, static_url_path="", static_folder="public")
CORS(app)

api_key = "b234bb351a835b67c4f8ce412a8e77ab"
api_secret = "d20ed987dd240464d6f4bd92af7247de"

#Purchase Notif
def send_email(data):
    email = data['email']
    name = data['account_name'] 
    textcontent = "You have bought {} for ${}\n Transaction ID: {}".format(data['game_title'], data['game_price'], data['purchase_id'])
    message = {
        "Messages": [
            {
                "From": {
                    "Email": "luden.gamestore@gmail.com",
                    "Name": "Luden Gamestore",
                },
                "To": [
                    {"Email": email, "Name": name}
                ],
                "Subject": "Game purchased",
                "TextPart": "Purchase notification",
                "HTMLPart": textcontent,
                "CustomID": "paymentnotif",
            }
        ]
    }
    print(message)
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    result = mailjet.send.create(data=message)
    # return (result.status_code)
    return result.json()

#Purchase fail notif
def send_failure_email(data):
    email = data['email']
    name = data['account_name']
    textcontent = "An error has occured for your payment. Please try again."
    message = {
        "Messages": [
            {
                "From": {
                    "Email": "luden.gamestore@gmail.com",
                    "Name": "Luden Gamestore",
                },
                "To": [
                    {"Email": email, "Name": name}
                ],
                "Subject": "Payment failed",
                "TextPart": "Payment failed",
                "HTMLPart": textcontent,
                "CustomID": "paymentnotif",
            }
        ]
    }
    print(message)
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    result = mailjet.send.create(data=message)
    # return (result.status_code)
    return result.json()

#Refund notif
def send_refund_email(data):
    email = data['email']
    name = data['account_name']
    textcontent = f"<h1>Hello {name}</h1> </br> We've issued the refund to your bank account. Depending on the bank's processing time, it can take anywhere from 5-10 business days to show up on your bank account. Thank you! </br> <h3>{data['game_title']}</h3> </br> Transaction ID: {data['purchase_id']} </br> Total refund: {data['game_price']} to your bank account"
    message = {
        "Messages": [
            {
                "From": {
                    "Email": "luden.gamestore@gmail.com",
                    "Name": "Luden Gamestore",
                },
                "To": [
                    {"Email": email, "Name": name}
                    
                ],
                "Subject": "Refund Processed",
                "TextPart": "Refund",
                "HTMLPart": textcontent,
                "CustomID": "refundnotif",
            }
        ]
    }
    print(message)
    mailjet = Client(auth=(api_key, api_secret), version="v3.1")
    result = mailjet.send.create(data=message)
    # return (result.status_code)
    return result.json()


a_queue_name = 'Notification_Log' # queue to be subscribed by Notification_Log microservice
payment_failure_queue_name = 'Notification_Log_Fail'
refund_queue_name = 'Notification_Refund'

def receiveNotificationLog(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=a_queue_name, on_message_callback=callback, auto_ack=True)
        print('notification_log: Consuming from queue:', a_queue_name)
        channel.basic_consume(queue=payment_failure_queue_name, on_message_callback=callbackfailure, auto_ack=True)
        print('notification_log: Consuming from queue:', payment_failure_queue_name)
        channel.basic_consume(queue=refund_queue_name, on_message_callback=callbackrefund, auto_ack=True)
        print('notification_log: Consuming from queue:', refund_queue_name)
        channel.start_consuming()  # an implicit loop waiting to receive messages;
             #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"notification_log: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("notification_log: Program interrupted by user.") 


def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nnotification_log: Received an notification log by " + __file__)
    processOrderLog(json.loads(body))
    print()

def callbackfailure(channel, method, properties, body): # required signature for the callback; no return
    print("\nnotification_log: Received a failure notification log by " + __file__)
    processFailureLog(json.loads(body))
    print()

def callbackrefund(channel, method, properties, body): # required signature for the callback; no return
    print("\nnotification_log: Received a refund notification log by " + __file__)
    processRefundLog(json.loads(body))
    print()

def processOrderLog(notification):
    print("notification_log: Recording an notification log:")
    print(notification)
    send_email(notification)
    print("sent email!")

def processFailureLog(notification):
    print("notification_log: Recording a failure notification log:")
    print(notification)
    send_failure_email(notification)
    print("sent email!")

def processRefundLog(notification):
    print("notification_log: Recording a refund notification log:")
    print(notification)
    send_refund_email(notification)
    print("sent email!")

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("notification_log: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("notification_log: Connection established successfully")
    channel = connection.channel()
    receiveNotificationLog(channel)



