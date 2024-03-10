import stripe
import json
import os

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    send_from_directory,
    redirect,
)
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS

load_dotenv(find_dotenv())

os.environ["STATIC_DIR"] = "/Applications/MAMP/htdocs/ESD/Project/ESD/Frontend/dist"

# For sample support and debugging, not required for production:
stripe.set_app_info(
    "stripe-samples/accept-a-payment/custom-payment-flow",
    version="0.0.2",
    url="https://github.com/stripe-samples",
)

stripe.api_version = "2020-08-27"
stripe.api_key = "sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6"

static_dir = str(os.path.abspath(os.path.join(__file__, "..", os.getenv("STATIC_DIR"))))
app = Flask(
    __name__,
    static_folder="/Applications/MAMP/htdocs/ESD/Project/ESD/Frontend/dist",
    static_url_path="",
    template_folder=static_dir,
)
CORS(app)


@app.route("/", methods=["GET"])
def get_root():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/config", methods=["GET"])
def get_config():
    return jsonify({"publishableKey": os.getenv("STRIPE_PUBLISHABLE_KEY")})


@app.route("/create-payment-intent", methods=["POST"])
def create_payment():
    
    data = request.json
    print(data)
    amount = 10000

    try:

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            payment_method=data['paymentMethodid']
            # Add more parameters as needed
        )
        print('LOL')
        print(payment_intent.client_secret)
        return jsonify(payment_intent), 200
    except Exception as e:
        print('fuck la')
        return jsonify(error=str(e)), 500
    
@app.route("/receive", methods=["POST"])
def receive_data():
    data = request.json  # Assuming the data is sent in JSON format
    # Process the data as needed
    print("Received data:", data)
    # You can return a response if needed
    totalprice = 0
    for game in data:
        totalprice += float(game["price"])
    print(totalprice)

    return redirect(url_for("create_payment_intent", totalprice=totalprice))

@app.route("/payment/next", methods=["GET"])
def get_payment_next():
    payment_intent = request.args.get("payment_intent")
    intent = stripe.PaymentIntent.retrieve(payment_intent)
    return redirect("/success?payment_intent_client_secret={intent.client_secret}")


@app.route("/success", methods=["GET"])
def get_success():
    return render_template("success.html")


@app.route("/webhook", methods=["POST"])
def webhook_received():
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get("stripe-signature")
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret
            )
            data = event["data"]
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event["type"]
    else:
        data = request_data["data"]
        event_type = request_data["type"]
    data_object = data["object"]

    if event_type == "payment_intent.succeeded":
        print("💰 Payment received!")
        # Fulfill any orders, e-mail receipts, etc
        # To cancel the payment you will need to issue a Refund (https://stripe.com/docs/api/refunds)
    elif event_type == "payment_intent.payment_failed":
        print("❌ Payment failed.")
    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(port=4242, debug=True)
