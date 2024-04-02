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
    'title': 'Shop microservice API',
    'version': 2.0,
    "openapi": "3.0.2",
    'description': 'Allows create, retrieve, update, and delete of shop items',
    'tags': {
        'Games': 'Operations related to game management',
        'Customizations': 'Operations related to customizations',
    },
    'ui_params': {
        'apisSorter': 'alpha',
        'operationsSorter': 'alpha',
        'tagsSorter': 'alpha',
    },
    'ui_params_text': '''{
        "tagsSorter": (a, b) => {
            const order = ['Users', 'Customisations'];
            return order.indexOf(a) - order.indexOf(b);
        }
    }''',
    
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
    wishlist_and_purchase_URL = "http://user:5600/users/" + str(userId) + "/wishlist-and-purchases"

    # INVOKE USER MICROSERVICE TO GET USER WISHLIST AND PURCHASE
    print("\n-----Invoking user microservice-----")
    wishlist_and_purchase_result = invoke_http(wishlist_and_purchase_URL)
    print("wishlist_and_purchase_result:", wishlist_and_purchase_result)

    wishlist_and_purchase_result_code = wishlist_and_purchase_result["code"]
    wishlist_and_purchase_message = json.dumps(wishlist_and_purchase_result)

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
    print("\n-----Invoking shop microservice-----")
    games_genre_result = invoke_http(game_genres_URL, method="POST", json=wishlist_and_purchase_result["data"])
    print("games_genre_result:", games_genre_result)

    games_genre_result_code = games_genre_result["code"]
    games_genre_message = json.dumps(games_genre_result)

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
    print("\n-----Invoking recommend microservice-----")
    common_genre_result = invoke_http(common_genre_URL, method="POST", json=games_genre_result["data"])
    print("common_genre_result:", common_genre_result)

    common_genre_result_code = common_genre_result["code"]
    common_genre_message = json.dumps(common_genre_result)

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


    # INVOKE shop MICROSERVICE TO GET GAMES THAT MATCHES COMMON GENRE
    print("\n-----Invoking shop microservice-----")
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

    games_by_genre_result = invoke_http(games_by_genre_URL)
    print("games_by_genre_result:", games_by_genre_result)

    games_by_genre_result_code = games_by_genre_result["code"]
    games_by_genre_message = json.dumps(games_by_genre_result)

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