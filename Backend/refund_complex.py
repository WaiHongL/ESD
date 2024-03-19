from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Define the microservices URLs
USER_MICROSERVICE_URL = 'http://localhost:5012/user'
POINTS_MICROSERVICE_URL = 'http://localhost:5333/points'
PAYMENT_MICROSERVICE_URL = 'http://localhost:5129/payment'
ERROR_MICROSERVICE_URL = 'http://localhost:5445/error' 

@app.route('/refund', methods=['POST'])
def process_refund():
    data = request.json
    user_id = data['user_id']
    game_id = data['game_id']
    points_to_deduct = data.get('points_to_deduct')

    # Step 1: Retrieve user gameplay time
    gameplay_time_response = requests.get(f"{USER_MICROSERVICE_URL}/gameplay-time/{user_id}/{game_id}")
    if gameplay_time_response.status_code != 200:
        return jsonify({"error": "Failed to get gameplay time."}), 500
    gameplay_time = gameplay_time_response.json().get('data', {}).get('gameplay_time')

    # Step 2: Check for refund eligibility
    if gameplay_time >= 120:
        # Log the error with the Error Microservice
        error_data = {
            'user_id': user_id,
            'game_id': game_id,
            'gameplay_time': gameplay_time
        }
        requests.post(f"{ERROR_MICROSERVICE_URL}/log", json=error_data)
        return jsonify({"error": "Refund ineligible due to gameplay time."}), 400

    # Step 3: Get user points
    user_points_response = requests.get(f"{POINTS_MICROSERVICE_URL}/points/{user_id}")
    if user_points_response.status_code != 200:
        return jsonify({"error": "Failed to get user points."}), 500
    user_points = user_points_response.json().get('points')

    # Step 4: Check if points are sufficient
    if user_points < points_to_deduct:
        return jsonify({"error": "Insufficient points."}), 400

    # Step 5: Deduct points for the refund
    update_points_data = {'user_id': user_id, 'points_to_deduct': points_to_deduct}
    points_update_response = requests.post(f"{POINTS_MICROSERVICE_URL}/points/update", json=update_points_data)
    if points_update_response.status_code != 200:
        return jsonify({"error": "Failed to update points."}), 500

    # Step 6: Process the refund through Stripe
    payment_intent_id = gameplay_time_response.json().get('data', {}).get('payment_intent')
    refund_data = {'payment_intent': payment_intent_id}
    payment_response = requests.post(f"{PAYMENT_MICROSERVICE_URL}/refund", json=refund_data)
    if payment_response.status_code != 200:
        return jsonify({"error": "Failed to process refund through Stripe."}), 500

    # If everything is successful, return confirmation
    return jsonify({"message": "Refund processed successfully."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)
