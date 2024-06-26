import stripe
import os, sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger

import json

stripe.api_key = "sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6"

app = Flask(__name__)
CORS(app)

# Initialize flasgger for API Documentation
app.config['SWAGGER'] = {
    'title': 'Payment Microservice API',
    'version': 2.0,
    "openapi": "3.0.2",
    'description': 'Allows users to process payments and refunds using Stripe API',
    'tags': {
        'Payment': 'Operations related to payment processing',
    },
}
swagger = Swagger(app)

@app.route("/payment", methods=['POST'])
def payment():
    """
    Process a payment
    ---
    tags:
        - ['Payment']
    requestBody:
        description: Payment details
        required: true
        content:
            application/json:
                schema:
                    properties:
                        purchase_id:
                            type: string
                            description: Purchase ID
                        price:
                            type: number
                            description: Price of the purchase
    responses:
        200:
            description: Payment processed successfully
        400:
            description: Invalid JSON input
        500:
            description: Internal server error
    """
    if request.is_json:
        data = request.get_json()
        data = json.loads(data)
        purchase_id = data['purchase_id']
        price = data['price']

        try:
            paymentintent = stripe.PaymentIntent.create(
                amount=int(float(price) * 100),
                currency="usd",
                automatic_payment_methods={"enabled": True},
                payment_method=purchase_id
            )
            paymentintend_id = paymentintent['id']
            confirmation = stripe.PaymentIntent.confirm(
                paymentintend_id,
                payment_method=purchase_id,
                return_url="https://www.google.com",
            )
            return jsonify(
                {   
                    "code": 200,
                    "data": confirmation
                }
            ), 200

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while processing payment"
                }
            ), 500
    
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


@app.route("/refund", methods=['POST'])
def refund():
    """
    Process a refund
    ---
    tags:
        - ['Payment']
    requestBody:
        description: Refund details
        required: true
        content:
            application/json:
                schema:
                    properties:
                        payment_intent:
                            type: string
                            description: Payment intent ID
    responses:
        200:
            description: Refund processed successfully
        400:
            description: Invalid JSON input
        500:
            description: Internal server error
    """
    if request.is_json:
        try:
            data = request.get_json()
            pi = data['payment_intent']
            refund_obj = stripe.Refund.create(payment_intent=pi)
            status = refund_obj['status']

            if status == 'succeeded':
                return jsonify(
                {   
                    "code": 200,
                    "data": refund_obj,
                }
            ), 200

            else:
                return jsonify(
                {   
                    "code": 400,
                    "message": 'Refund failed'
                }
            ), 400

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while refunding payment"
                }
            ), 500
    
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5604)