from flask import Flask, request, jsonify
from invokes import invoke_http
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Define the microservices URLs
USER_MICROSERVICE_URL = 'http://localhost:5101'
PAYMENT_MICROSERVICE_URL = 'http://localhost:5666'
ERROR_MICROSERVICE_URL = 'http://localhost:5445/error' 
SHOP_CUSTOMIZATION_MICROSERVICE_URL = 'http://localhost:5000'

def log_error(user_id, error_message):
    #Function to log errors to the Error Microservice.
    error_data = {'user_id': user_id, 'error_message': error_message}
    invoke_http(f"{ERROR_MICROSERVICE_URL}/log", method='POST', json=error_data)

@app.route('/refund', methods=['POST'])
def process_refund():
    #Pull data first
    print(request.get_json())
    if request.is_json:
        try:
            data = request.get_json()
            print(data)
            user_id = data['user_id']
            game_id = data['game_id']
            purchase_id = data['purchase_id']
            gamedetail = invoke_http(f"{SHOP_CUSTOMIZATION_MICROSERVICE_URL}/games/{game_id}", method='GET')
            if gamedetail['code'] not in range(200,300):
                log_error(game_id, "Failed to get game")
                return jsonify({"error": "Failed to get game."}), 500
            print(gamedetail)

            points_to_deduct = gamedetail['data']['points']
            print("points to deduct:")
            print(points_to_deduct)

            # Step 1: Retrieve user's gameplay time
            gameplay_time_response = invoke_http(f"{USER_MICROSERVICE_URL}/gameplay-time/{user_id}/{game_id}", method='GET')
            if gameplay_time_response['code'] not in range(200,300):
                log_error(user_id, "Failed to get gameplay time")
                return jsonify({"error": "Failed to get gameplay time."}), 500
            gameplay_time = gameplay_time_response['data']['gameplay_time']
            print("gameplay time:")
            print(gameplay_time)

            # Step 2: Check for refund eligibility
            if gameplay_time and gameplay_time >= 120:
                log_error(user_id, "Refund ineligible due to gameplay time")
                print("gameplay more than 2 hours")
                return jsonify({"error": "Refund ineligible due to gameplay time."}), 400

            # Step 3: Get user points
            user_response = invoke_http(f"{USER_MICROSERVICE_URL}/users/{user_id}", method='GET')
            if user_response['code'] not in range(200,300):
                log_error(user_id, "Failed to get user")
                return jsonify({"error": "Failed to get user."}), 500
          
    
            user_points = user_response['data']['points']
            print("user points:")
            print(user_points)

            # Step 4: Check if points are sufficient
                
            if user_points >= points_to_deduct:
                # invoke user.py endpoint that only updates the points
                points_to_change = {'operation': '-', 'price': points_to_deduct/100}
                update_points_result = invoke_http(f"{USER_MICROSERVICE_URL}/users/{user_id}/points/update", method='PUT', json=points_to_change)
                if update_points_result['code'] != 200:
                    log_error(user_id, "Failed to update user points")
                    return jsonify({"error": "Failed to update user points."}), 500
            else:
                remaining = points_to_deduct - user_points
                print("remaining points to deduct:")
                print(remaining)

                user_item_purchase_history = invoke_http(f"{USER_MICROSERVICE_URL}/users/{user_id}/customizations", method='GET')
                print(user_item_purchase_history)
                #error handle if cant retrieve
                if user_item_purchase_history['code'] not in range(200,300):
                    log_error(user_id, "Failed to retrieve user item purchase history")
                    return jsonify({"error": "Failed to retrieve user item purchase history."}), 500
                
                user_item_purchase_history_list = user_item_purchase_history['data']
                print("items user owns:")
                print(user_item_purchase_history_list)
                customizations = invoke_http(f"{SHOP_CUSTOMIZATION_MICROSERVICE_URL}/customizations", method='GET')
                if customizations['code'] not in range(200,300):
                    log_error(user_id, "Failed to retrieve customizations")
                    return jsonify({"error": "Failed to retrieve customizations."}), 500
                
                customizations_list = customizations['data']['customizations']
                customizations_dict={}
                for customization in customizations_list:
                    customizations_dict[customization['customization_id']] = customization['credits']
                print("custom dict:")
                print(customizations_dict)


                list_to_run = []
                for item in user_item_purchase_history_list:
                    item_tuple = (item['customization_id'],customizations_dict[item['customization_id']])
                    list_to_run.append(item_tuple)
                print("all of user items:")
                print(list_to_run)

                to_remove_list=[]

                print(list_to_run[-1][1])
                while (remaining > 0) and (len(list_to_run) > 0):
                    print("remaining:")
                    print(remaining)
                    print('last item pointa')
                    print(list_to_run[-1][1])
                    remaining -= list_to_run[-1][1]
                    last_customization = list_to_run.pop() 
                    to_remove_list.append(last_customization[0])
                    print(to_remove_list)
                print('items to remove:')
                print(to_remove_list)
                
                change_points = user_points + remaining
                print('points to deduct')
                print(change_points)
                operation='minus'
          
                customizations_to_delete = {'user_id':user_id,'to_remove_list':to_remove_list}
                delete_customizations = invoke_http(f"{USER_MICROSERVICE_URL}/customizations/delete", method='DELETE',json = customizations_to_delete)
                print(delete_customizations)
                if delete_customizations['code'] not in range(200,300):
                        log_error(user_id, "Failed to delete customizations")
                        return jsonify({"error": "Failed to delete customizations."}), 500
                print('items deleted successfully')
                points_to_change = {'operation':operation,'price':abs(change_points/100)}
                update_points_result = invoke_http(f"{USER_MICROSERVICE_URL}/users/{user_id}/points/update",method='PUT', json=points_to_change)
                print(update_points_result)
                if update_points_result['code'] not in range(200,300):
                        log_error(user_id, "Failed to update points after deleting customizations")
                        return jsonify({"error": "Failed to update points after deleting customizations."}), 500
                print('points deducted successfully')
                print('success')
            
            # Step 5: Delete purchase record
            del_json = {'user_id':user_id,'game_id':game_id}
            delete_purchase_record = invoke_http(f"{USER_MICROSERVICE_URL}/game-purchase/delete", method = 'DELETE', json = del_json)
            print(delete_purchase_record)
            if delete_purchase_record['code'] != 200:
                return jsonify({"error": "Failed to delete purchase record."}), 500
            # the error handling above cannot uncomment. If i uncomment, it doesnt run to the next part
            
            # Step 6: Process the refund through Stripe
            payment_intent_id = purchase_id
            refund_data = {'payment_intent': payment_intent_id}
            payment_response = invoke_http(f"{PAYMENT_MICROSERVICE_URL}/refund",method='POST', json=refund_data)
            print(payment_response)
            if payment_response['code'] != 200:
                return jsonify({"error": "Failed to process refund through Stripe."}), 500



            # If everything is successful, return confirmation
            return jsonify({"message": "Refund processed successfully."}), 200
        except:
            return {'code': '400'}
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)
