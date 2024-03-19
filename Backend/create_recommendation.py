from flask import Flask, jsonify
from flask_cors import CORS

from invokes import invoke_http
import amqp_connection
import json
import pika
import sys

app = Flask(__name__)
CORS(app)

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
game_URL = "http://localhost:5000/games"
game_genres_URL = "http://localhost:5000/games/genre"
common_genre_URL = "http://localhost:5300/recommend/genre"

# CREATE RECOMMENDATION
@app.route("/recommendations/<int:userId>")
def create_recommendations(userId):
    try:
        result = process_recommendation(userId)
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "create_recommendation.py internal error"
        }), 500

def process_recommendation(userId):
    wishlist_and_purchase_URL = "http://localhost:5101/users/" + str(userId) + "/wishlist-and-purchases"

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


    # INVOKE SHOP MICROSERVICE TO GET GAMES GENRE
    print("\n-----Invoking shop microservice-----")
    games_genre_result = invoke_http(game_genres_URL, method="POST", json=wishlist_and_purchase_result)
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
    common_genre_result = invoke_http(common_genre_URL, method="POST", json=games_genre_result)
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


    # INVOKE GAME MICROSERVICE TO GET GAMES THAT MATCHES COMMON GENRE
    print("\n-----Invoking game microservice-----")
    genre = common_genre_result["data"]
    game_by_genre_URL = "http://localhost:5000/games?genre=" + genre
    game_by_genre_result = invoke_http(game_by_genre_URL)
    print("game_by_genre_result:", game_by_genre_result)

    game_by_genre_result_code = game_by_genre_result["code"]
    game_by_genre_message = json.dumps(game_by_genre_result)

    if game_by_genre_result_code not in range(200, 300):
        print("\n\n-----Publishing the (game by genre error) message with routing_key=game.by.genre.error-----")

        channel.basic_publish(
            exchange = exchangename,
            routing_key = "game.by.genre.error",
            body = game_by_genre_message,
            properties = pika.BasicProperties(delivery_mode = 2)
        )

        print("\Game by genre error published to the RabbitMQ Exchange:".format(game_by_genre_result_code), game_by_genre_result)

        return {
            "code": 500,
            "data": { "game_by_genre_result": game_by_genre_result },
            "message": "Game by genre error sent for error handling."
        }

    return game_by_genre_result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)