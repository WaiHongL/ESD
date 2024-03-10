from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF@34.124.211.169/user'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    account_name = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    points = db.Column(db.Float)

    def __init__(self, user_id, email, account_name, password, points):
        self.user_id = user_id
        self.email = email
        self.account_name = account_name
        self.password = password
        self.points = points

    def json(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "account_name": self.account_name,
            "password": self.password,
            "points": self.points
        }

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

class GamePurchase(db.Model):
    __tablename__ = 'gamepurchase'

    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    game_id = db.Column(db.Integer, nullable=False, primary_key = True)
    purchase_id = db.Column(db.String, nullable = True)

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

    def json(self):
        return {
            "purchase_id": self.purchase_id,
            "game_id": self.game_id,
            "user_id": self.user_id
        }
    
# GET USER CART AND PURCHASE
@app.route("/users/<int:userId>")
def get_user_cart_and_purchase(userId):
    user = db.session.scalars(db.select(User).filter_by(user_id=userId)).all()

    if (user):
        wishlist = db.session.scalars(db.select(Wishlist).filter_by(user_id=userId)).all()
        purchaseList = db.session.scalars(db.select(Purchase).filter_by(user_id=userId)).all()

        if (len(wishlist) or len(purchaseList)):
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
    return jsonify(
        {
            "code": 404,
            "message": "User does not exist."
        }
    ), 404

# DELETE PURCHASE RECORD IN GAME PURCHASE TABLE
@app.route("/delete-game-purchase", methods=['DELETE'])
def delete_game_purchase():
    return
    
# UPDATE PURCHASE RECORD IN GAME PURCHASE TABLE
@app.route("/update-game-purchase", methods=['PUT'])
def update_game_purchase():
    try:
        data = request.get_json(force=True)
        print(data)
        user_id = data['user_id']
        print(user_id)
        game_id = data['game_id']
        print(game_id)
        purchase_id = data['transaction_id']
        print(purchase_id)
        purchase = db.session.scalars(db.select(GamePurchase).filter_by(user_id= user_id, game_id= game_id)).first()
        
        print(purchase)
        if purchase:
            purchase.purchase_id = purchase_id # Replace new_purchase_id with the actual new value
            db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "error": str(e),
                "message": "An error occurred updating the game purchase."
            }
        ), 500
    return jsonify(
    {
        "code": 200,
    }
), 200

# CREATE A PURCHASE RECORD IN GAME PURCHASE TABLE
@app.route("/game-purchase", methods=['POST'])
def create_game_purchase():
    print("user service")
    data = request.get_json(force=True)
   
    print(type(data))
    game = GamePurchase(**data)

    try:
        db.session.add(game)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "error": str(e),
                "message": "An error occurred creating the game."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": game.json()
        }
    ), 201

#GET USER DETAILS
@app.route("/userdetail/<int:userId>")
def get_user_details(userId):
    user = db.session.scalars(db.select(User).filter_by(user_id=userId)).one()
    if (user):
        print(user)
        return jsonify(
            {
                "code": 200,
                "data": {
                    'user_id': user.user_id,
                    'account_name': user.account_name,
                    'email': user.email
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no such user."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5101, debug=True)