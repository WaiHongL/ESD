from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF:@34.142.233.183/shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Game(db.Model):
    __tablename__ = 'game'

    game_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    points = db.Column(db.Integer, primary_key=True)

    def __init__(self, game_id, title, genre, price, points):
        self.game_id = game_id
        self.title = title
        self.genre = genre
        self.price = price
        self.points = points

    def json(self):
        return {
            "game_id": self.game_id,
            "title": self.title,
            "genre": self.genre,
            "price": self.price,
            "points": self.points
        }
    
# GET ALL GAMES AND GAMES BY GENRE
@app.route("/games")
def get_all_games():
    # CHECK IF "GENRE" IS IN QUERY PARAMS
    if (request.args.get("genre")):
        genre = request.args.get("genre")
        gameList = db.session.scalars(db.select(Game).filter_by(genre=genre)).all()

        if len(gameList):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "games": [game.json() for game in gameList]
                    }
                }
            )

        return jsonify(
            {
                "code": 404,
                "message": "There are no games that matches the genre."
            }
        ), 404
    
    # FOR FRONTEND
    gameList = db.session.scalars(db.select(Game)).all()

    if len(gameList):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "games": [game.json() for game in gameList]
                }
            }
        )
    
    return jsonify(
        {
            "code": 404,
            "message": "There are no games."
        }
    ), 404

# GET GAME GENRES
@app.route("/games/genre", methods=["POST"])
def get_games_genre():
    if request.is_json:
        data = request.get_json()["data"]
        wishlist_data = []
        purchase_data = []

        if "wishlist" in data:
            wishlist_data = data["wishlist"]

        if "purchases" in data:
            purchase_data = data["purchases"]
        
        # CONCATENATE cart_data AND purchase_data
        data_arr = wishlist_data + purchase_data
        games_id_arr = []

        for data in data_arr:
            for key, value in data.items():
                if (key == "game_id" or key == "item_id") and value not in games_id_arr:
                    games_id_arr.append(value)

        # GET GENRES
        genres = []
        for game_id in games_id_arr:
            game = db.session.scalars(db.select(Game).filter_by(game_id=game_id).limit(1)).first()
            if (game):
                genre = game.genre
                genres.append(genre)

        if len(genres) > 0:
            return jsonify(
                {
                    "code": 200,
                    "data": genres
                }
            )
        else:
            return jsonify(
                {
                    "code": 404,
                    "data": "There are no game genres."
                }
            )
        
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    })

#GET GAME DETAILS
@app.route("/gamedetail/<int:gameId>")
def get_game_details(gameId):
    game = db.session.scalars(db.select(Game).filter_by(game_id=gameId)).one()
    if (game):
        print(game)
        return jsonify(
            {
                "code": 200,
                "data": {
                    'game_id': game.game_id,
                    'title': game.title,
                    'price': game.price
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is no such game."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)