from flask import Flask, request, jsonify
from invokes import invoke_http
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Define the microservices URLs
USER_MICROSERVICE_URL = 'http://localhost:5101'
PAYMENT_MICROSERVICE_URL = 'http://localhost:5129/payment'
ERROR_MICROSERVICE_URL = 'http://localhost:5445/error' 
SHOP_CUSTOMIZATION_MICROSERVICE_URL = 'http://localhost:5000/customizations'

@app.route('/refund', methods=['POST'])
def process_refund():
    #Pull data first
    data = request.json
    user_id = data['user_id']
    game_id = data['game_id']
    points_to_deduct = data.get('points_to_deduct')

    # Step 1: Retrieve user's gameplay time, GET request to fetch
    gameplay_time_response = requests.get(f"{USER_MICROSERVICE_URL}/gameplay-time/{user_id}/{game_id}")
    #testing if gameplay status code is successful
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

    # Step 3: Get user points, invoke GET to fetch it
    user_points_response = requests.get(f"{POINTS_MICROSERVICE_URL}/points/{user_id}")
    if user_points_response.status_code != 200:
        return jsonify({"error": "Failed to get user points."}), 500
    user_points = user_points_response.json().get('points')

    # Step 4: Check if points are sufficient, need the points to deduct from points.py
    
    if user_points >= points_to_deduct:
        # invoke user.py endpoint that only updates the points
        points_to_change = {'operation':'-','price':points_to_deduct/100}
        update_points_result = invoke_http(f"{USER_MICROSERVICE_URL}/users/{user_id}/points/update",methods=['PUT'], json=points_to_change)
        # handle error
    else:
        remaining = points_to_deduct - user_points

        user_item_purchase_history = invoke_http(f"{USER_MICROSERVICE_URL}/{user_id}/customizations")
        user_item_purchase_history_list = user_item_purchase_history['data']

        customizations = invoke_http(SHOP_CUSTOMIZATION_MICROSERVICE_URL)
        customizations_list = customizations['data']['customizations']
        customizations_dict={}
        for customization in customizations_list:
            customizations_dict[customization['customization_id']] = customization['credits']
        print(customizations_dict)

        list_to_run = []
        for item in user_item_purchase_history_list:
            item_tuple = (item['customization_id'],customizations_dict[item['customization_id']])
            list_to_run.append(item_tuple)
        print(list_to_run)

        to_remove_list=[]
        
        while remaining > list_to_run[-1][1]:
            remaining = remaining - list_to_run[-1][1]
            last_customization = list_to_run.pop() 
            to_remove_list.append(last_customization[0])

        new_points = last_customization[1] - remaining
        change_points = new_points - user_points

        if change_points>=0:
            operation = 'add'
        else:
            operation='minus'

        customizations_to_delete = {'user_id':user_id,'to_remove_list':to_remove_list}
        delete_customizations = invoke_http(f"{USER_MICROSERVICE_URL}/customizations/delete", methods=['DELETE'],json = customizations_to_delete)
        #error handling
        
        points_to_change = {'operation':operation,'price':abs(change_points/100)}
        update_points_result = invoke_http(f"{USER_MICROSERVICE_URL}/users/{user_id}/points/update",methods=['PUT'], json=points_to_change)
        #error handling

        #invoke user.py endpoint to update points and delete customoizations from customization table
     

   

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
