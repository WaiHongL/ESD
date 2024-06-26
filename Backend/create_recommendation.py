from flask import Flask, jsonify
from flask_cors import CORS
from flasgger import Swagger

from invokes import invoke_http
import amqp_connection
import json
import pika
import sys
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# Initialize flasgger for API Documentation
app.config['SWAGGER'] = {
    'title': 'Create Recommendation Microservice API',
    'version': 2.0,
    "openapi": "3.0.2",
    'description': 'Orchestrate the creation of recommendations for a user',
    'tags': {
        'Games': 'Operations related to game management',
        'Customizations': 'Operations related to customizations',
    },
}

swagger = Swagger(app)

# AMQP
exchangename = "order_topic" # exchange name
exchangetype="topic" # use a 'topic' exchange to enable interaction
connection = amqp_connection.create_connection() 
channel = connection.channel()

# If the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

# URL
game_URL = "http://kong:8000/shop/games"
game_genres_URL = "http://kong:8000/shop/games/genre"
common_genre_URL = "http://kong:8000/recommend/genre"

# CREATE RECOMMENDATION
@app.route("/create-recommendation/<int:userId>")
def create_recommendation(userId):
    """
    Creates recommendations of games for a user
    ---
    tags:
      - Recommendations
    parameters:
      - name: userId
        in: path
        type: integer
        required: true
        description: The ID of the user to create a recommendation for
    responses:
      200:
        description: Recommendation created successfully
      500:
        description: Internal server error
    """
    try:
        result = process_recommendation(userId)
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "create_recommendation.py internal error"
            }
        ), 500

def process_recommendation(userId):
    # Technical robustness
    num_retries = 0
    max_retries = 5

    shouldRetry = True

    wishlist_and_purchase_result = {}
    wishlist_and_purchase_result_code = 400
    wishlist_and_purchase_message = ""

    games_genre_result = {}
    games_genre_result_code = 400
    games_genre_message = ""

    common_genre_result = {}
    common_genre_result_code = 400
    common_genre_message = ""

    games_by_genre_result = {}
    games_by_genre_result_code = 400
    games_by_genre_message = ""
    
    wishlist_and_purchase_URL = "http://kong:8000/users/" + str(userId) + "/wishlist-and-purchases"

    # INVOKE USER MICROSERVICE TO GET USER WISHLIST AND PURCHASE
    while num_retries < max_retries and wishlist_and_purchase_result_code not in range(200, 300) and shouldRetry == True:
        print("\n-----Invoking user microservice-----")
        wishlist_and_purchase_result = invoke_http(wishlist_and_purchase_URL)
        print("wishlist_and_purchase_result:", wishlist_and_purchase_result)

        if "message" in wishlist_and_purchase_result and len(wishlist_and_purchase_result) == 2:
            shouldRetry = True

            if num_retries + 1 == max_retries:
                wishlist_and_purchase_message = json.dumps(wishlist_and_purchase_result)
        else: 
            shouldRetry = False
            wishlist_and_purchase_result_code = wishlist_and_purchase_result["code"]
            wishlist_and_purchase_message = json.dumps(wishlist_and_purchase_result)

        num_retries += 1

    # Reset
    shouldRetry = True
    num_retries = 0

    if wishlist_and_purchase_result_code not in range(200, 300):
        print("\n\n-----Publishing the (wishlist and purchase error) message with routing_key=wishlist.purchase.error-----")

        channel.basic_publish(
            exchange = exchangename,
            routing_key = "wishlist.purchase.error",
            body = wishlist_and_purchase_message,
            properties = pika.BasicProperties(delivery_mode = 2)
        )

        print("\nWishlist and purchase error published to the RabbitMQ Exchange:".format(wishlist_and_purchase_result_code), wishlist_and_purchase_result)

        return {
            "code": 500,
            "data": { "wishlist_and_purchase_result": wishlist_and_purchase_result },
            "message": "Wishlist and purchase error sent for error handling."
        }
    
    # GET GAME IDS OF PURCHASES
    wishlist_and_purchase_data = wishlist_and_purchase_result["data"]
    wishlist_ids = []
    if "wishlist" in wishlist_and_purchase_data:
        wishlist = wishlist_and_purchase_data["wishlist"]
        for wish in wishlist:
            wishlist_ids.append(wish["game_id"])

    purchase_ids = []
    if "purchases" in wishlist_and_purchase_data:
        purchases = wishlist_and_purchase_data["purchases"]
        for purchase in purchases:
            purchase_ids.append(purchase["game_id"])

    # INVOKE SHOP MICROSERVICE TO GET GAMES GENRE
    while num_retries < max_retries and games_genre_result_code not in range(200, 300) and shouldRetry == True:
        print("\n-----Invoking shop microservice-----")
        games_genre_result = invoke_http(game_genres_URL, method="POST", json=wishlist_and_purchase_result["data"])
        print("games_genre_result:", games_genre_result)

        if "message" in games_genre_result and len(games_genre_result) == 2 and games_genre_result["message"] != "There are no game genres" and "Invalid JSON input" not in games_genre_result["message"]:
            shouldRetry = True

            if num_retries + 1 == max_retries:
                games_genre_message = json.dumps(games_genre_result)
        else: 
            shouldRetry = False
            games_genre_result_code = games_genre_result["code"]
            games_genre_message = json.dumps(games_genre_result)

        num_retries += 1

    # Reset
    shouldRetry = True
    num_retries = 0

    if games_genre_result_code not in range(200, 300):
        print("\n\n-----Publishing the (games genre error) message with routing_key=games.genre.error-----")

        channel.basic_publish(
            exchange = exchangename,
            routing_key = "games.genre.error",
            body = games_genre_message,
            properties = pika.BasicProperties(delivery_mode = 2)
        )

        print("\nGames genre error published to the RabbitMQ Exchange:".format(games_genre_result_code), games_genre_result)

        return {
            "code": 500,
            "data": { "games_genre_result": games_genre_result },
            "message": "Games genre error sent for error handling."
        }
    

    # INVOKE RECOMMEND MICROSERVICE TO GET COMMON GENRE
    while num_retries < max_retries and common_genre_result_code not in range(200, 300) and shouldRetry == True:
        print("\n-----Invoking recommend microservice-----")
        common_genre_result = invoke_http(common_genre_URL, method="POST", json=games_genre_result["data"])
        print("common_genre_result:", common_genre_result)

        if "message" in common_genre_result and len(common_genre_result) == 2 and "Invalid JSON input" not in common_genre_result["message"]:
            shouldRetry = True

            if num_retries + 1 == max_retries:
                common_genre_message = json.dumps(common_genre_result)
        else: 
            shouldRetry = False
            common_genre_result_code = common_genre_result["code"]
            common_genre_message = json.dumps(common_genre_result)

        num_retries += 1

    # Reset
    shouldRetry = True
    num_retries = 0

    if common_genre_result_code not in range(200, 300):
        print("\n\n-----Publishing the (common genre error) message with routing_key=common.genre.error-----")

        channel.basic_publish(
            exchange = exchangename,
            routing_key = "common.genre.error",
            body = common_genre_message,
            properties = pika.BasicProperties(delivery_mode = 2)
        )

        print("\nCommon genre error published to the RabbitMQ Exchange:".format(common_genre_result_code), common_genre_result)

        return {
            "code": 500,
            "data": { "common_genre_result": common_genre_result },
            "message": "Comnmon genre error sent for error handling."
        }


    # INVOKE SHOP MICROSERVICE TO GET GAMES THAT MATCHES COMMON GENRE
    genre = common_genre_result["data"]
    games_by_genre_URL = "http://kong:8000/shop/games?genre="

    if type(genre) is list:
        for i in range(len(genre)):
            if i == 0:
                games_by_genre_URL += quote(genre[i])
            else:
                games_by_genre_URL += "&genre=" + quote(genre[i])
    else:
        games_by_genre_URL += quote(genre)

    while num_retries < max_retries and games_by_genre_result_code not in range(200, 300) and shouldRetry == True:
        print("\n-----Invoking shop microservice-----")
        games_by_genre_result = invoke_http(games_by_genre_URL)
        print("games_by_genre_result:", games_by_genre_result)

        if "message" in games_by_genre_result and len(games_by_genre_result) == 2 and games_by_genre_result["message"] != "There are no games" and "An error occurred" not in games_by_genre_result["message"]:
            shouldRetry = True

            if num_retries + 1 == max_retries:
                games_by_genre_message = json.dumps(games_by_genre_result)
        else: 
            shouldRetry = False
            games_by_genre_result_code = games_by_genre_result["code"]
            games_by_genre_message = json.dumps(games_by_genre_result)

        num_retries += 1

    # Reset
    shouldRetry = True
    num_retries = 0

    if games_by_genre_result_code not in range(200, 300):
        print("\n\n-----Publishing the (game by genre error) message with routing_key=game.by.genre.error-----")

        channel.basic_publish(
            exchange = exchangename,
            routing_key = "game.by.genre.error",
            body = games_by_genre_message,
            properties = pika.BasicProperties(delivery_mode = 2)
        )

        print("\nGame by genre error published to the RabbitMQ Exchange:".format(games_by_genre_result_code), games_by_genre_result)

        return {
            "code": 500,
            "data": { "games_by_genre_result": games_by_genre_result },
            "message": "Game by genre error sent for error handling."
        }
    
    # FILTER GAMES ALREADY PURCHASED
    games_by_genre_data = games_by_genre_result["data"]
    recommended_games = []
    if "games" in games_by_genre_data:
        games = games_by_genre_data["games"]
        for game in games:
            if (game["game_id"] not in purchase_ids and game["game_id"] not in wishlist_ids):
                recommended_games.append(game)
    
    games_by_genre_result["data"]["games"] = recommended_games

    return games_by_genre_result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5603, debug=True)