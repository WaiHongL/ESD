from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF@34.124.211.169/user"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    account_name = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    points = db.Column(db.Float)
    selected_customization_id = db.Column(db.Integer)

    def __init__(self, user_id, email, account_name, password, points, selected_customization_id):
        self.user_id = user_id
        self.email = email
        self.account_name = account_name
        self.password = password
        self.points = points
        self.selected_customization_id = selected_customization_id

    def json(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "account_name": self.account_name,
            "password": self.password,
            "points": self.points,
            "selected_customization_id": self.selected_customization_id
        }


class Wishlist(db.Model):
    __tablename__ = "wishlist"

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


class GamePurchase(db.Model):
    __tablename__ = "gamepurchase"

    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    game_id = db.Column(db.Integer, nullable=False, primary_key=True)
    purchase_id = db.Column(db.String, nullable=True)
    gameplay_time = db.Column(db.Integer, nullable=True, default = 0)

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

    def json(self):
        return {
            "game_id": self.game_id,
            "user_id": self.user_id,
            "purchase_id": self.purchase_id,
            "gameplay_time": self.gameplay_time,
        }
    
class CustomizationPurchase(db.Model):
    __tablename__ = "customization_purchase"

    purchase_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    customization_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, customization_id):
        self.user_id = user_id
        self.customization_id = customization_id

    def json(self):
        return {
            "purchase_id": self.purchase_id,
            "customization_id": self.customization_id,
            "user_id": self.user_id
        }


# GET USER WISHLIST AND PURCHASES
@app.route("/users/<int:userId>/wishlist-and-purchases")
def get_wishlist_and_purchase(userId):
    try:
        user = db.session.scalars(db.select(User).filter_by(user_id=userId)).all()

        if user:
            wishlist = db.session.scalars(
                db.select(Wishlist).filter_by(user_id=userId)
            ).all()
            purchase_list = db.session.scalars(
                db.select(GamePurchase).filter_by(user_id=userId)
            ).all()

            if len(wishlist) or len(purchase_list):
                if len(wishlist) and not len(purchase_list):
                    data = {"wishlist": [cart.json() for cart in wishlist]}
                elif len(purchase_list) and not len(wishlist):
                    data = {
                        "purchases": [purchase.json() for purchase in purchase_list]
                    }
                else:
                    data = {
                        "wishlist": [cart.json() for cart in wishlist],
                        "purchases": [purchase.json() for purchase in purchase_list],
                    }

                return jsonify({
                    "code": 200, 
                    "data": data
                })

            return (
                jsonify(
                    {
                        "code": 404,
                        "message": "There are no games in user wishlist and purchase records.",
                    }
                ),
                404,
            )

        return jsonify({
            "code": 404, 
            "message": "User does not exist."
        }), 404

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while getting user wishlist and purchases.",
            }
        )
    

# GET USER CUSTOMIZATIONS
@app.route("/users/<int:userId>/customizations")
def get_customizations(userId):
    try:
        user = db.session.scalars(db.select(User).filter_by(user_id=userId)).all()

        if user:
            customizations_list = db.session.scalars(
                db.select(CustomizationPurchase).filter_by(user_id=userId)
            ).all()

            if len(customizations_list):
                return jsonify({
                    "code": 200, 
                    "data": [customization.json() for customization in customizations_list]
                })

            return (
                jsonify(
                    {
                        "code": 404,
                        "message": "There are no customizations available.",
                    }
                ),
                404,
            )

        return jsonify({
            "code": 404, 
            "message": "User does not exist."
        }), 404

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while getting user customizations.",
            }
        )


# UPDATE PURCHASE RECORD IN GAME PURCHASE TABLE
@app.route("/update-game-purchase", methods=["PUT"])
def update_game_purchase():
    try:
        data = request.get_json(force=True)
        print(data)
        user_id = data["user_id"]
        print(user_id)
        game_id = data["game_id"]
        print(game_id)
        purchase_id = data["transaction_id"]
        print(purchase_id)
        purchase = db.session.scalars(
            db.select(GamePurchase).filter_by(user_id=user_id, game_id=game_id)
        ).first()

        print(purchase)
        if purchase:
            purchase.purchase_id = (
                purchase_id  # Replace new_purchase_id with the actual new value
            )
            db.session.commit()
    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": str(e),
                    "message": "An error occurred updating the game purchase.",
                }
            ),
            500,
        )
    return (
        jsonify(
            {
                "code": 200,
            }
        ),
        200,
    )


# CREATE A PURCHASE RECORD IN GAME PURCHASE TABLE
@app.route("/game-purchase", methods=["POST"])
def create_game_purchase():
    print("user service")
    data = request.get_json(force=True)
    print(data)
    print(type(data))
    game = GamePurchase(**data)

    try:
        db.session.add(game)
        db.session.commit()
    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "error": str(e),
                    "message": "An error occurred creating the game.",
                }
            ),
            500,
        )

    return jsonify({"code": 201, "data": game.json()}), 201


# DELETE A PURCHASE RECORD
@app.route("/game-purchase/<int:userid>/<int:gameid>", methods=["DELETE"])
def delete_game_purchase(userid, gameid):
    # Query the database for the purchase entry
    purchase = GamePurchase.query.filter_by(user_id=userid, game_id=gameid).first()
    
    # Check if the purchase entry exists
    if purchase:
        # Delete the purchase entry
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({"code": 200, "message": "Purchase entry deleted successfully"}), 200
    else:
        return jsonify({"code": 404, "message": "Purchase entry not found"}), 404


# GET USER DETAILS
@app.route("/userdetail/<int:userId>")
def get_user_details(userId):
    user = db.session.scalars(db.select(User).filter_by(user_id=userId)).one()
    if user:
        print(user)
        return jsonify(
            {
                "code": 200,
                "data": {
                    "user_id": user.user_id,
                    "account_name": user.account_name,
                    "email": user.email,
                },
            }
        )
    return jsonify({"code": 404, "message": "There is no such user."}), 404


# GET USER DETAILS (NEW)
@app.route("/users/<int:userId>")
def get_user_details_new(userId):
    user = db.session.scalars(db.select(User).filter_by(user_id=userId)).one()
    if user:
        return jsonify(
            {
                "code": 200,
                "data": user.json()
            }
        )
    return jsonify({
        "code": 404, 
        "message": "There is no such user."
    }), 404


@app.route("/gameplay-time/<int:userId>/<int:gameId>", methods = ["GET"])
def get_purchase_records(userId, gameId):
    record = db.session.scalars(db.select(GamePurchase).filter_by(user_id=userId,game_id=gameId)).one()
    if record:
        print(record)
        return jsonify(
            {
                "code":200,
                "data": {
                    "user_id": record.user_id,
                    "game_id": record.game_id,
                    "payment_intent": record.purchase_id,
                    "gameplay_time": record.gameplay_time,
                },
            }
        )
    return jsonify({"code": 404, "message": "There is no such record."}), 404



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101, debug=True)


