from flask import Flask, jsonify
from flask_cors import CORS

from invokes import invoke_http

app = Flask(__name__)
CORS(app)

game_URL = "http://localhost:5000/games"
game_genres_URL = "http://localhost:5000/games/genre"
common_genre_URL = "http://localhost:5300/recommend/genre"

# CREATE RECOMMENDATION
@app.route("/recommendations/<int:userId>")
def get_recommendations(userId):
    cart_and_purchase_URL = "http://localhost:5101/users/" + str(userId) + "/cart-and-purchases"

    # 1. INVOKE USER MICROSERVICE TO GET USER CART AND PURCHASE
    print("\n-----Invoking user microservice-----")
    cart_and_purchase_result = invoke_http(cart_and_purchase_URL)
    cart_and_purchase_result_code = cart_and_purchase_result["code"]
    print("cart_and_purchase_result:", cart_and_purchase_result)

    if cart_and_purchase_result_code not in range(200, 300):
        return cart_and_purchase_result


    # 2. INVOKE SHOP MICROSERVICE TO GET GAMES GENRE
    print("\n-----Invoking shop microservice-----")
    games_genre_result = invoke_http(game_genres_URL, method="POST", json=cart_and_purchase_result)
    print("games_genre_result:", games_genre_result)

    if games_genre_result not in range(200, 300):
        return games_genre_result


    # 3. INVOKE RECOMMEND MICROSERVICE TO GET COMMON GENRE
    print("\n-----Invoking recommend microservice-----")
    common_genre_result = invoke_http(common_genre_URL, method="POST", json=games_genre_result)
    print("common_genre_result:", common_genre_result)

    if common_genre_result not in range(200, 300):
        return common_genre_result


    # 4. INVOKE GAME MICROSERVICE TO GET GAMES THAT MATCHES COMMON GENRE
    print("\n-----Invoking game microservice-----")
    genre = common_genre_result["data"]
    game_by_genre_URL = "http://localhost:5000/games?genre=" + genre
    game_by_genre_result = invoke_http(game_by_genre_URL)
    print("game_by_genre_result:", game_by_genre_result)


    return game_by_genre_result


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5500, debug=True)