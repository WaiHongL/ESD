from flask import Flask, request, jsonify

app = Flask(__name__)

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
