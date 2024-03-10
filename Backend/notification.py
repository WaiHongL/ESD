from mailjet_rest import Client
from flask import Flask, redirect, request
import amqp_connection
import json
import pika
from flask_cors import CORS

app = Flask(__name__, static_url_path="", static_folder="public")
CORS(app)

api_key = "ebf8fab91654b14ea8cb67d7899fd7eb"
api_secret = "9b1132c0970817650f7e33fb8a345618"

def send_email(data):
    email = data['email']
    name = data['account_name']
    textcontent = "You have bought {} for ${}\n Transaction ID: {}".format(data['title'], data['price'], data['transactionid'])
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







a_queue_name = 'Notification_Log' # queue to be subscribed by Activity_Log microservice

# Instead of hardcoding the values, we can also get them from the environ as shown below
# a_queue_name = environ.get('Activity_Log') #Activity_Log

def receiveNotificationLog(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=a_queue_name, on_message_callback=callback, auto_ack=True)
        print('notification_log: Consuming from queue:', a_queue_name)
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

def processOrderLog(notification):
    print("notification_log: Recording an notification log:")
    print(notification)
    send_email(notification)
    print("sent email!")

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("notification_log: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("activity_log: Connection established successfully")
    channel = connection.channel()
    receiveNotificationLog(channel)



