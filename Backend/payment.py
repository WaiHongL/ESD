from flask import Flask, redirect, request
import stripe

app = Flask(__name__, static_url_path="", static_folder="public")


stripe.api_key = "sk_test_51LrjcfK1WW7DRh3qSpVCT1CWMxeC8bpxPOQdTWJ6SyFCJCSpt6opHUXb1QqB65u8zvxdrmkzYqNcZy2TBHoSzjX000cRwCOEA6"

YOUR_DOMAIN = "http://localhost:4242"


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "F-shirt",
                        },
                        "unit_amount": 5000,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=YOUR_DOMAIN + "/success.html",
            cancel_url=YOUR_DOMAIN + "/cancel.html",
        )
        
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route("/view")
def view_all_session():
    return stripe.PaymentIntent.list()


if __name__ == "__main__":
    app.run(port=4242, debug=True)
