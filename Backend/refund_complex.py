from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URLs for the other microservices, need to edit accordingly
USER_MICROSERVICE_URL = 'http://localhost:5277/users'
TIME_MICROSERVICE_URL = 'http://localhost:5999/checktime'
POINT_MICROSERVICE_URL = ''
ERROR_MICROSERVICE_URL = 'http://localhost:5445/error'


@app.route('/refund', methods=['POST'])

def process_refund():
    data = request.json
    user_id = data['user_id']
    game_id = data['game_id']

    # Step 2: Send user info to User Microservice to get gameplay time
    try:
        gameplay_time_response = requests.get(f"{USER_MICROSERVICE_URL}/gameplay-time/{user_id}/{game_id}")
        gameplay_time_response.raise_for_status()
    except requests.RequestException as e:
        # Log e
        return jsonify({"error": "Failed to get gameplay time."}), 500

    gameplay_time = gameplay_time_response.json().get('gameplay_time')

    # Step 4 and 5: Check with Time Microservice if gameplay time is less than 2 hours
    try:
        refund_eligibility_response = requests.get(f"{TIME_MICROSERVICE_URL}/check-time", params={'gameplayTime': gameplay_time})
        refund_eligibility_response.raise_for_status()
    except requests.RequestException as e:
        # Log e
        return jsonify({"error": "Failed to check time eligibility."}), 500

    is_eligible_for_refund = refund_eligibility_response.json().get('eligibleForRefund')

    # Step 8: If gameplay time is more than 2 hours, the refund is ineligible
    if not is_eligible_for_refund:
        try:
            error_response = requests.post(f"{ERROR_MICROSERVICE_URL}/refund-eligibility", json=data)
            error_response.raise_for_status()
        except requests.RequestException as e:
            # Log e
            pass  # Error microservice call failed, decide how to handle this. need to come up with error microservice
        return jsonify({"error": "Refund ineligible due to gameplay time."}), 400

    # Step 6 and 7: If eligible, get the user's points
    try:
        user_points_response = requests.get(f"{USER_MICROSERVICE_URL}/points/{user_id}")
        user_points_response.raise_for_status()
    except requests.RequestException as e:
        # Log e
        return jsonify({"error": "Failed to get user points."}), 500

    user_points = user_points_response.json().get('points')
    points_to_deduct = data['points_to_deduct']

    # Step 9 and 11: Deduct points if sufficient
    if user_points >= points_to_deduct:
        try:
            update_points_response = requests.post(f"{POINT_MICROSERVICE_URL}/points/update", json=data)
            update_points_response.raise_for_status()
            # Proceed with Stripe refund, NEED CAIJUN HELP
        except requests.RequestException as e:
            # Log e
            return jsonify({"error": "Failed to update user points."}), 500

    # Handle insufficient points in some way IDK HELPS
    # ...

    # If everything is successful, return confirmation, need AMQP
    return jsonify({"message": "Refund processed successfully."}), 200

    #check the logic behind point.copy()
    
    #the action move to user.py 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)
