from flask import Flask, request, jsonify

app = Flask(__name__)

user_points = {}

@app.route('/points', methods=['GET'])
def get_user_points(user_id):
    if user_id not in user_points:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'points': user_points[user_id]})

@app.route('/points/update', methods=['POST'])
def update_points():
    try:
        # Get data from the request
        data = request.json
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
            'user_id': user_id,
            'new_points': user_points[user_id]
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error updating points: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5600)
