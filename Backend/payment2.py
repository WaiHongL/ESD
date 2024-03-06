import stripe
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS

stripe.api_key = "sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6"

app = Flask(__name__, static_url_path="", static_folder="public")
CORS(app)

@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=2000,
            currency="usd",
            automatic_payment_methods={"enabled": True},
        )
    except Exception as e:
        return str(e)
    return jsonify({"clientSecret": payment_intent.client_secret})


@app.route("/receive", methods=["POST"])
def receive_data():
    data = request.json  # Assuming the data is sent in JSON format
    # Process the data as needed
    print("Received data:", data)
    # You can return a response if needed
    return jsonify({"message": "Data received successfully"})


if __name__ == "__main__":
    app.run(port=4242, debug=True)
