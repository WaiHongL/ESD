from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:password@luden-user.cbki4scc2nyk.ap-southeast-1.rds.amazonaws.com/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Cart(db.Model):
    __tablename__ = 'cart'

    game_title = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, game_title):
        self.user_id = user_id
        self.game_title = game_title

    def json(self):
        return {
            "game_title": self.game_title,
            "user_id": self.user_id
        }
    
class Purchase(db.Model):
    __tablename__ = 'purchase'

    game_title = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, game_title):
        self.user_id = user_id
        self.game_title = game_title

    def json(self):
        return {
            "game_title": self.game_title,
            "user_id": self.user_id
        }
    
# GET USER CART AND PURCHASE
@app.route("/users/<int:userId>")
def get_user_cart_and_purchase(userId):
    cartList = db.session.scalars(db.select(Cart).filter_by(user_id=userId)).all()
    purchaseList = db.session.scalars(db.select(Purchase).filter_by(user_id=userId)).all()

    if (len(cartList) and len(purchaseList)):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "cart": [cart.json() for cart in cartList],
                    "purchase": [purchase.json() for purchase in purchaseList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no games in cart."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)