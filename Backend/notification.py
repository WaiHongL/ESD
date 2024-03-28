from mailjet_rest import Client
from flask import Flask, redirect, request
import amqp_connection
import json
import pika
from flask_cors import CORS
import base64

app = Flask(__name__, static_url_path="", static_folder="public")
CORS(app)

api_key = "b234bb351a835b67c4f8ce412a8e77ab"
api_secret = "d20ed987dd240464d6f4bd92af7247de"


# Path to your image file
#image_path = "..\\Frontend\\src\\assets\\images\\home\\luden_logo.jpg"

# Read the image file and encode it in base64
# with open(image_path, 'rb') as image_file:
#     encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

#Purchase Notif
def send_email(data):
    email = data['email']
    name = data['account_name'] 
    # img = "../Frontend/src/assets/images/home/ludengame.png"
    textcontent = """
    
        <!DOCTYPE html>
        <html>
        <head>
            <title>Game Purchase Confirmation</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 5px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="" alt="Luden Gamestore Logo" style="max-width: 150px; height: auto;">
                </div>
                <div style="background-color: #d4edda; border-color: #c3e6cb; border-radius: 5px; padding: 20px; margin-bottom: 20px;">
                    <h2 style="color: #155724; margin: 0 0 15px;">Congratulations on Your Purchase!</h2>
                    <p style="margin: 0 0 15px;">You have successfully purchased <strong>{}</strong> for <strong>${}</strong>.</p>
                    <p style="margin: 0 0 15px;">Your Transaction ID is: <strong>{}</strong></p>
                </div>
                <div style="text-align: center;">
                    <a href="http://localhost:5173/user" style="display: inline-block; background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 16px;">Download Your Game</a>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <p style="color: #6c757d; margin: 0;">If you have any questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """.format(data['game_title'], data['game_price'], data['purchase_id'])
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
    textcontent = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Failure Notification</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 5px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="" alt="Luden Gamestore Logo" style="max-width: 150px; height: auto;">
                </div>
                <div style="background-color: #f9dede; border-color: #f5c6cb; border-radius: 5px; padding: 20px; margin-bottom: 20px;">
                    <h2 style="color: #d8000c; margin: 0 0 15px;">Payment Failure</h2>
                    <p style="margin: 0 0 15px;">An error has occurred with your payment. Please try again.</p>
                </div>
                <div style="text-align: center;">
                    <a href="http://localhost:5173/" style="display: inline-block; background-color: #007bff; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 16px;">Go to Shop</a>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <p style="color: #6c757d; margin: 0;">If you have any questions, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
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
    textcontent = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Refund Confirmation</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff; border-radius: 5px;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="" alt="Luden Gamestore Logo" style="max-width: 150px; height: auto;">
                </div>
                <div style="background-color: #d4edda; border-color: #c3e6cb; border-radius: 5px; padding: 20px; margin-bottom: 20px;">
                    <h2 style="color: #155724; margin: 0 0 15px;">Refund Processed Successfully</h2>
                    <p style="margin: 0 0 15px;">Hello {name},</p>
                    <p style="margin: 0 0 15px;">We're pleased to inform you that the refund for your purchase has been successfully processed and will be credited to your bank account. Depending on your bank's processing time, it may take anywhere from 5-10 business days for the refund to appear in your account.</p>
                    <p style="margin: 0 0 15px;">Thank you for your understanding and patience. We hope you'll consider Luden Gamestore for your future gaming needs.</p>
                    <h3 style="margin: 0 0 15px;">Refund Details:</h3>
                    <p style="margin: 0 0 15px;">Game Title: <strong>{data['game_title']}</strong></p>
                    <p style="margin: 0 0 15px;">Transaction ID: <strong>{data['purchase_id']}</strong></p>
                    <p style="margin: 0 0 15px;">Total Refund: <strong>${data['game_price']}</strong></p>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <p style="color: #6c757d; margin: 0;">If you have any questions or need further assistance, please contact our support team.</p>
                </div>
            </div>
        </body>
        </html>
        """
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



