import stripe
import os, sys
from flask import Flask, request, jsonify
from flask_cors import CORS

import json

stripe.api_key = "sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6"

app = Flask(__name__)
CORS(app)

@app.route("/payment", methods=['POST'])
def payment():
    if request.is_json:
        data = request.get_json()
        # print(json.loads(data))
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
            # print(confirmation)
            return jsonify(
                {   
                    "code": 200,
                    "data": confirmation
                }
            ), 200

        except Exception as e:
            # Unexpected error in code
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)

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
    if request.is_json:
        try:
            data = request.get_json()
            #data = json.loads(data)
            print(data)
            pi = data['payment_intent']
            print(pi)
            refund_obj = stripe.Refund.create(payment_intent=pi)
            status = refund_obj['status']
            if status == 'succeeded':
                return jsonify(
                {   
                    "code": 200,
                    "data": 'Refund successful'
                }
            ), 200
            else:
                return jsonify(
                {   
                    "code": 500,
                    "data": 'Refund failed (Stripe error)'
                }
            ), 200
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while refunding payment"
                }
            ), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5666)