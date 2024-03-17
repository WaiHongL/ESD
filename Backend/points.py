from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import os, sys
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF@34.124.211.169/user'
app.config['SQLALCHEMY_BINDS'] = {'shop': 'mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF:@34.142.233.183/shop'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
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
    
class Game(db.Model):
    __bind_key__ = 'shop'
    __tablename__ = 'game'  

    game_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    points = db.Column(db.Integer, primary_key=True)

    def __init__(self, game_id, title, genre, price, points):
        self.game_id = game_id
        self.title = title
        self.genre = genre
        self.price = price
        self.points = points

    def json(self):
        return {
            "game_id": self.game_id,
            "title": self.title,
            "genre": self.genre,
            "price": self.price,
            "points": self.points
        }
    
class Customizations(db.Model):
    __bind_key__ = 'shop'
    __tablename__ = 'customizations'  

    customization_id = db.Column(db.Integer, primary_key=True)
    tier = db.Column(db.String(255), nullable=False)
    credits = db.Column(db.Integer, primary_key=True)

    def __init__(self, customization_id, tier, credits):
        self.customization_id = customization_id
        self.tier = tier
        self.credits = credits

    def json(self):
        return {
            "customization_id": self.customization_id,
            "tier": self.tier,
            "credits": self.credits,
        }

user_points = {}

@app.route('/points/<string:user_id>', methods=['GET'])
def get_user_points(user_id):
    if user_id not in user_points:
        return jsonify({'message': 'User not found'}), 404
    refund_amount = request.args.get('refund_amount', default=None, type=int)

    if refund_amount is not None:
        return jsonify({'user_id': user_id, 'refund_amount': refund_amount})
    else:
        return jsonify({'user_id': user_id, 'points': user_points[user_id]})


@app.route('/points/add', methods=['POST'])
def add_points():
    # if request.is_json:
        # print(request.json())
        try:
            pointjson = request.json
           
            user = User.query.get(pointjson['user_id'])
            if user:
                user.points = user.points + (float(pointjson['price']) *100)
                db.session.commit()
                return json.dumps({
                "code": 200,
                "message": "Points successfully added"
            }), 200
            return json.dumps({
                "code": 400,
                "message": "Invalid user"
            }), 400

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return json.dumps({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500
    

@app.route('/points/update', methods=['POST'])
def update_points():
    try:
        data = request.json
        
        user_id = data.get('user_id')
        game_id = data.get('game_id')
        customization_id = data.get('customization_id')
        
        # Retrieve user and game from the database using Session.get()
        session = Session()
        user = session.query(User).get(user_id)
        game = session.query(Game).get(game_id)
        customization = session.query(Customizations).get(customization_id)
        
        if not user or not game:
            return jsonify({'error': 'Invalid user ID or game ID'}), 400
        
        # Add points for customizations
        customizations_points = customization.credits
        user.points += customizations_points
        
        # Deduct game points
        game_points = game.points
        user.points -= game_points
        
        # Update user's points in the database
        db.session.commit()

        return jsonify({'message': 'Points updated successfully', 'user_points': user.points}), 200

    except Exception as e:
        print(f"Error updating points: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5600)
