from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger
from os import environ

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Initialize flasgger for API Documentation
app.config['SWAGGER'] = {
    'title': 'User microservice API',
    'version': 2.0,
    "openapi": "3.0.2",
    'description': 'Allows create, retrieve, update, and delete of users',
    'tags': {
        'Users': 'Operations related to user management',
        'Customizations': 'Operations related to customizations',
        'Game Purchase': 'Operations related to game purchases',
    },
    'ui_params': {
        'apisSorter': 'alpha',
        'operationsSorter': 'alpha',
        'tagsSorter': 'alpha',
    },
    'ui_params_text': '''{
        "tagsSorter": (a, b) => {
            const order = ['Users', 'Customizations'];
            return order.indexOf(a) - order.indexOf(b);
        }
    }''',
    
}

swagger = Swagger(app)

app.config["SQLALCHEMY_DATABASE_URI"] = environ.get('dbURL') or "mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF@34.124.211.169/user"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    account_name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default = 0)
    selected_customization_id = db.Column(db.Integer, nullable=True)

    def __init__(self, email, account_name, password, selected_customization_id):
        self.email = email
        self.account_name = account_name
        self.password = password
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

    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    game_id = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

    def json(self):
        return {
            "user_id": self.user_id,
            "game_id": self.game_id,
        }


class GamePurchase(db.Model):
    __tablename__ = "game_purchase"

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

    purchase_id = db.Column(db.Integer, nullable=False, primary_key=True)
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


# GET USER DETAILS 
@app.route("/users/<int:userId>")
def get_user_details_new(userId):
    """
    Get user details by user ID
    ---
    tags:
        - ['Users']
    parameters:
        -   in: path
            name: userId
            required: true    
    responses:
        200:
            description: Returned user details successfully
        404:
            description: User not found
    """
    try:
        user = db.session.scalars(db.select(User).filter_by(user_id=userId)).one()
        if user:
            return jsonify(
                {
                    "code": 200,
                    "data": user.json()
                }
            ), 200
        
        return jsonify(
            {
                "code": 404, 
                "data": {
                    "user_id": userId
                },
                "message": "There is no such user"
            }
        ), 404
    # The code 404 will not return I tried on Postman. If i query for user id = 10, the code below is returned instead.
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while getting user details"
            }
        ), 500
    

# UPDATE USER POINTS
@app.route("/users/<int:userId>/points/update", methods=["PUT"])
def update_points(userId):
    # """
    # Update user points
    # ---
    # tags:
    #     - ['Users']
    # requestBody:
    #     description: Points update operation
    #     required: true
    #     content:
    #         application/json:
    #             schema:
    #                 properties:
    #                     operation: 
    #                         type: string
    #                         description: Operation type (add or subtract)
    #                     price: 
    #                         type: number
    #                         description: Price for the operation
    # responses:
    #     200:
    #         description: Points updated successfully
    #     404:
    #         description: User not found
    #     500:
    #         description: Internal server error
    # """
    if request.is_json:
        try:
            points_json = request.get_json()

            user = User.query.get(userId)

            if user:
                if points_json["operation"] == "add":
                    user.points  = user.points + (float(points_json["price"]) * 100)
                else:
                    user.points  = user.points - (float(points_json["price"]) * 100)

                db.session.commit()
                return jsonify(
                    {
                        "code": 200,
                        "data": user.json()
                    }
                ), 200
            
            return jsonify(
                {
                    "code": 404, 
                    "data": {
                        "user_id": userId
                    },
                    "message": "User does not exist"
                }
            ), 404

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while updating user points"
                }
            ), 500
        
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


# GET USER WISHLIST AND PURCHASES
@app.route("/users/<int:userId>/wishlist-and-purchases")
def get_wishlist_and_purchase(userId):
    """
    Get user wishlist and purchases
    ---
    tags:
        - ['Users']
    parameters:
        -   in: path
            name: userId
            required: true
    responses:
        200:
            description: Returned user wishlist and purchases successfully
        404:
            description: User not found or no wishlist/purchases
    """    
    try:
        user = db.session.scalars(db.select(User).filter_by(user_id=userId)).all()

        if user:
            wishlist = db.session.scalars(db.select(Wishlist).filter_by(user_id=userId)).all()
            purchase_list = db.session.scalars(db.select(GamePurchase).filter_by(user_id=userId)).all()

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
                        "purchases": [purchase.json() for purchase in purchase_list]
                    }

                return jsonify(
                    {
                        "code": 200, 
                        "data": data
                    }
                ), 200

            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "user_id": userId
                    },
                    "message": "There are no games in user wishlist and purchase records"
                }
            ), 404

        return jsonify(
            {
                "code": 404, 
                "data": {
                    "user_id": userId
                },
                "message": "User does not exist"
            }
        ), 404

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while getting user wishlist and purchases"
            }
        ), 500
    

# ADD TO WISHLIST
@app.route("/users/wishlist/create", methods=["POST"])
def create_wishlist():
    """
    Create wishlist record
    ---
    tags:
        - ['Users']
    responses:
        201:
            description: Wishlist entry created
        400:
            description: Invalid JSON input
        500:
            description: Internal server error
    """
    if request.is_json:
        data = request.get_json()
        wish = Wishlist(**data)

        try:
            db.session.add(wish)
            db.session.commit()

            return jsonify(
                {
                    "code": 201, 
                    "data": wish.json()
                }
            ), 201

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while creating the wishlist record"
                }
            ), 500
    
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


# DELETE FROM WISHLIST
@app.route("/users/wishlist/delete", methods=["DELETE"])
def delete_wishlist(): 
    """
    Delete a wishlist entry
    ---
    tags:
        - ['Users']
    responses:
        200:
            description: Wishlist entry deleted 
        404:
            description: Wishlist entry not found
        500:
            description: Internal server error
    """    
    if request.is_json:
        try:
            data = request.get_json()
            print(data)
            user_id = data["user_id"]
            game_id = data["game_id"]

            wish = Wishlist.query.filter_by(user_id=user_id, game_id=game_id).first()
            
            # Check if the purchase entry exists
            if wish:
                # Delete the purchase entry
                db.session.delete(wish)
                db.session.commit()
                return jsonify(
                    {
                        "code": 200, 
                        "message": "Wish record deleted"
                    }
                ), 200
            else:
                return jsonify(
                    {
                        "code": 404, 
                        "message": "Wish record not found"
                    }
                ), 404
            
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred deleting the wish record"
                }
            ), 500
        
    return jsonify(
        {
            "code": 400, 
            "data": {
                "user_id": user_id
            },
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400
    

# GET USER CUSTOMIZATIONS
@app.route("/users/<int:userId>/customizations")
def get_customizations(userId):
    """
    Get user customizations
    ---
    tags:
        - ['Users']
    parameters:
        -   in: path
            name: userId
            required: true
    responses:
        200:
            description: Returned user customizations successfully
        404:
            description: User not found or no customizations
    """
    try:
        user = db.session.scalars(db.select(User).filter_by(user_id=userId)).all()

        if user:
            customizations_list = db.session.scalars(db.select(CustomizationPurchase).filter_by(user_id=userId)).all()

            if len(customizations_list):
                return jsonify(
                    {
                        "code": 200, 
                        "data": [customization.json() for customization in customizations_list]
                    }
                ), 200

            return jsonify(
                    {
                        "code": 404,
                        "data": {
                            "user_id": userId
                        },
                        "message": "User does not have any customizations"
                    }
            ), 404
            
        return jsonify(
            {
                "code": 404, 
                "message": "User does not exist"
            }
        ), 404

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while getting user customizations"
            }
        ), 500
    

# UPDATE USER SELECTED CUSTOMIZATION
@app.route("/users/customizations/update", methods=["PUT"])
def update_customization():
    """
    Update user selected customization
    ---
    tags:
        - ['Users']
    requestBody:
        description: Customization update details
        required: true
        content:
            application/json:
                schema:
                    properties:
                        user_id: 
                            type: integer
                            description: User ID
                        customization_id: 
                            type: integer
                            description: Customization ID
    responses:
        200:
            description: Customization updated successfully
        404:
            description: User not found
        500:
            description: Internal server error
    """
    if request.is_json:
        try:
            data = request.get_json()
            user_id = data["user_id"]
            customization_id = data["customization_id"]

            user = User.query.get(user_id)

            if user:
                user.selected_customization_id = customization_id
                db.session.commit()
                return jsonify(
                    {
                        "code": 200,
                        "data": user.json()
                    }
                ), 200
            
            return jsonify(
                {
                    "code": 404, 
                    "data": {
                        "user_id": user_id
                    },
                    "message": "User does not exist"
                }
            ), 404

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while updating user selected customization"
                }
            ), 500
        
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400
    

# DELETE CUSTOMIZATION RECORDS
@app.route("/customizations/delete", methods=["DELETE"])
def delete_customization():
    """
    Delete customization purchase records
    ---
    tags:
        - ['Customizations']
    responses:
        200:
            description: Customization purchase records deleted
        404:
            description: Customization purchase records not found
        500:
            description: Internal server error
    """
    if request.is_json:
        try:
            data = request.get_json()
            user_id = data["user_id"]
            to_remove_list = data["to_remove_list"]
            # Query the database for the purchase entry
            print(user_id)
            print(to_remove_list)
            customizationpurchase = CustomizationPurchase.query.filter(CustomizationPurchase.customization_id.in_(to_remove_list), CustomizationPurchase.user_id == user_id).delete()
            print(customizationpurchase)
            
            # Check if the purchase entry exists
            if customizationpurchase:
                # Delete the purchase entry
                
                db.session.commit()
                return jsonify(
                    {
                        "code": 200, 
                        "message": "Customization Purchase entry deleted successfully"
                    }
                ), 200
            else:
                return jsonify(
                    {
                        "code": 404, 
                        "message": "Customization Purchase entry not found"
                    }
                ), 404
            
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred deleting the customization purchase"
                }
            ), 500
        
    return jsonify(
        {
            "code": 400, 
            "data": {
                "user_id": user_id
            },
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


# CREATE A PURCHASE RECORD IN GAME PURCHASE TABLE
@app.route("/game-purchase/create", methods=["POST"])
def create_game_purchase():
    """
    Create a game purchase record
    ---
    tags:
        - ['Game-purchase']
    requestBody:
        description: Game purchase details
        required: true
        content:
            application/json:
                schema:
                    properties:
                        user_id: 
                            type: integer
                            description: User ID
                        game_id: 
                            type: integer
                            description: Game ID
                        purchase_id: 
                            type: string
                            description: Purchase ID
                        gameplay_time: 
                            type: integer
                            description: Gameplay time in minutes
    responses:
        201:
            description: Game purchase record created
        400:
            description: Invalid JSON input
        500:
            description: Internal server error
    """
    if request.is_json:
        data = request.get_json(force=True)
        game = GamePurchase(**data)

        try:
            db.session.add(game)
            db.session.commit()

            return jsonify(
                {
                    "code": 201, 
                    "data": game.json()
                }
            ), 201

        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while creating the game purchase record"
                }
            ), 500
    
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


# UPDATE PURCHASE RECORD IN GAME PURCHASE TABLE
@app.route("/game-purchase/update", methods=["PUT"])
def update_game_purchase():
    """
    Update a game purchase record
    ---
    tags:
        - ['Game-purchase']
    requestBody:
        description: Game purchase update details
        required: true
        content:
            application/json:
                schema:
                    properties:
                        user_id: 
                            type: integer
                            description: User ID
                        game_id: 
                            type: integer
                            description: Game ID
                        purchase_id: 
                            type: string
                            description: Purchase ID
                        gameplay_time: 
                            type: integer
                            description: Gameplay time in minutes
    responses:
        200:
            description: Game purchase record updated successfully
        404:
            description: Game purchase record not found
        500:
            description: Internal server error
    """
    if request.is_json:
        try:
            data = request.get_json(force=True)
            # print(data)
            user_id = data["user_id"]
            # print(user_id)
            game_id = data["game_id"]
            # print(game_id)
            purchase_id = data["transaction_id"]
            # print(purchase_id)

            purchase = db.session.scalars(
                db.select(GamePurchase).filter_by(user_id=user_id, game_id=game_id)
            ).first()

            # print(purchase)
            if purchase:
                purchase.purchase_id = (
                    purchase_id  # Replace new_purchase_id with the actual new value
                )
                db.session.commit()

                return jsonify(
                    {
                        "code": 200,
                        "data": purchase.json()
                    }
                ), 200
            
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred updating the game purchase"
                }
            ), 500
    
    return jsonify(
        {
            "code": 400, 
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


# DELETE A PURCHASE RECORD
@app.route("/game-purchase/delete", methods=["DELETE"])
def delete_game_purchase():
    """
    Delete a game purchase record
    ---
    tags:
        - ['Game-purchase']
    requestBody:
        description: Game purchase delete details
        required: true
        content:
            application/json:
                schema:
                    properties:
                        user_id: 
                            type: integer
                            description: User ID
                        game_id: 
                            type: integer
                            description: Game ID
    responses:
        200:
            description: Game purchase record deleted successfully
        404:
            description: Game purchase record not found
        500:
            description: Internal server error
    """
    if request.is_json:
        try:
            data = request.get_json()
            user_id = data["user_id"]
            game_id = data["game_id"]
            # Query the database for the purchase entry
            purchase = GamePurchase.query.filter_by(user_id=user_id, game_id=game_id).first()
            
            # Check if the purchase entry exists
            if purchase:
                # Delete the purchase entry
                db.session.delete(purchase)
                db.session.commit()
                return jsonify(
                    {
                        "code": 200, 
                        "message": "Purchase entry deleted successfully"
                    }
                ), 200
            else:
                return jsonify(
                    {
                        "code": 404, 
                        "message": "Purchase entry not found"
                    }
                ), 404
            
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred deleting the game purchase"
                }
            ), 500
        
    return jsonify(
        {
            "code": 400, 
            "data": {
                "user_id": user_id
            },
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


# # GET USER DETAILS
# @app.route("/userdetail/<int:userId>")
# def get_user_details(userId):
#     user = db.session.scalars(db.select(User).filter_by(user_id=userId)).one()
#     if user:
#         print(user)
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": {
#                     "user_id": user.user_id,
#                     "account_name": user.account_name,
#                     "email": user.email,
#                 },
#             }
#         )
#     return jsonify({"code": 404, "message": "There is no such user."}), 404

#Get gameplay time of game
@app.route("/game-purchase/<int:userId>/<int:gameId>", methods = ["GET"])
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

# Get payment ID for refund
# @app.route("/purchase-id/<int:userId>/<int:gameId>", methods = ["GET"])
# def get_purchase_id(userId,gameId):
#     record = db.session.scalars(db.select(GamePurchase).filter_by(user_id=userId,game_id=gameId)).one()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101, debug=True)


