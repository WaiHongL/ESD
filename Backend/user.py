from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@34.124.211.169/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    user_id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

    def json(self):
        return {
            "user_id": self.user_id,
            "game_id": self.game_id,
        }
    
class Purchase(db.Model):
    __tablename__ = 'purchase'

    purchase_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)

    def __init__(self, purchase_id, user_id, item_id):
        self.purchase_id = purchase_id
        self.user_id = user_id
        self.item_id = item_id

    def json(self):
        return {
            "purchase_id": self.purchase_id,
            "item_id": self.item_id,
            "user_id": self.user_id
        }
    
# GET USER CART AND PURCHASE
@app.route("/users/<int:userId>")
def get_user_cart_and_purchase(userId):
    wishlist = db.session.scalars(db.select(Wishlist).filter_by(user_id=userId)).all()
    purchaseList = db.session.scalars(db.select(Purchase).filter_by(user_id=userId)).all()

    if (len(wishlist) and len(purchaseList)):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "wishlist": [cart.json() for cart in wishlist],
                    "purchases": [purchase.json() for purchase in purchaseList]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no games in wishlist and purchase records."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)