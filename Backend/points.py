from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

import os, sys
import requests
import json

app = Flask(__name__)
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
    if request.is_json:
        try:
            pointjson = request.get_json()
            user = User.query.get(1)
            if user:
                user.points = user.points + (pointjson['price'] *100)
                db.session.commit()
                return jsonify({
                "code": 200,
                "message": "Points successfully added"
            }), 200
            return jsonify({
                "code": 400,
                "message": "Invalid user"
            }), 400



        
        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500
    



@app.route('/points/update', methods=['POST'])
def update_points():
    try:
        # Get data from the request
        data_array = request.json

        # Check if data is an array
        if not isinstance(data_array, list):
            raise ValueError('Invalid data format. Expected an array.')

        # Process each user in the array
        for data in data_array:
            # Check if required keys are present in the JSON payload
            required_keys = ['user_id', 'refund_amount']
            if not all(key in data for key in required_keys):
                raise ValueError('Missing required keys in JSON payload')

            user_id = data['user_id']
            refund_amount = data['refund_amount']

            # Check if user_id exists in user_points, initialize with 0 points if not
            user_points.setdefault(user_id, 0)

            # Check if the user has sufficient points to deduct
            if user_points[user_id] >= refund_amount:
                # Deduct points
                user_points[user_id] -= refund_amount
            else:
                # Add points to restore balance
                user_points[user_id] += refund_amount

        # Return the corrected user points
        response = {
            'message': 'Points updated successfully',
            'user_points': user_points
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error updating points: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5600)
