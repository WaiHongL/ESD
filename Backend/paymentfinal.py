import stripe
import os, sys
from flask import Flask, request
from flask_cors import CORS

import json
stripe.api_key = "sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6"
app = Flask(__name__)
CORS(app)
@app.route("/payment", methods=['POST'])
def payment():
    data = request.get_json()
    print(json.loads(data))
    data = json.loads(data)
    paymentmethod_id = data['paymentmethod_id']
    price = data['price']

    try:
        paymentintent = stripe.PaymentIntent.create(
        amount=int(float(price) * 100),
        currency="usd",
        automatic_payment_methods={"enabled": True},
        payment_method= paymentmethod_id
        )
        paymentintend_id = paymentintent['id']
        confirmation = stripe.PaymentIntent.confirm(
        paymentintend_id,
        payment_method=paymentmethod_id,
        return_url="https://www.google.com",
        )
        print(confirmation)
        return {"confirmation": confirmation,
                "code": 201
        }

    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)
        return {"code": 400}

@app.route("/refund", methods=['POST'])
def refund():
    refund_obj = stripe.Refund.create(payment_intent="pi_3Ov8sDK1WW7DRh3q1ypxFZr2")
    status = refund_obj['status']
    if status == 'succeeded':
        return #refund successful
    else:
        return #refund fail


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5666)