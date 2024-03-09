import stripe
from flask import Flask, redirect, request, jsonify, render_template, session, url_for
from flask_cors import CORS

stripe.api_key = "sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6"

app = Flask(__name__, static_url_path="", static_folder="public")
CORS(app)


@app.route("/create-payment-intent", methods=["POST"])
def create_payment_intent():
    totalprice = request.args.get("totalprice")
    print("hi")
    print(totalprice)
    print(float(totalprice))
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(float(totalprice)) * 100,
            currency="usd",
            confirmation_method="automatic",
        )
        print(payment_intent)
    except Exception as e:

        return str(e)

    return jsonify({"clientSecret": payment_intent.client_secret})


# @app.route('/checkout')
# def checkout():
#   intent = # ... Fetch or create the PaymentIntent
#   return render_template('checkout.html', client_secret=intent.client_secret)





if __name__ == "__main__":
    app.run(port=4242, debug=True)
