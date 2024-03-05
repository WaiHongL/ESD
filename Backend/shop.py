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
    
# GET ALL GAMES
@app.route("/games")
def get_all_games():
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

@app.route("/games", methods=["POST"])
def get_games_by_genre():
    genre = request.get_json()["data"]
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


# GET GAME GENRES
@app.route("/games/genre", methods=["POST"])
def get_games_genre():
    wishlist_data = request.get_json()["data"]["wishlist"]
    purchase_data = request.get_json()["data"]["purchases"]
    
    # CONCATENATE cart_data and purchase_data
    data_arr = wishlist_data + purchase_data
    id_arr = []

    for data in data_arr:
        for key, value in data.items():
            if (key == "game_id" or key == "item_id") and value not in id_arr:
                id_arr.append(value)

    # GET GENRES
    genres = []
    for id in id_arr:
        game = db.session.scalars(db.select(Game).filter_by(game_id=id).limit(1)).first()
        if (game):
            genre = game.genre
            genres.append(genre)
    
    return jsonify(
        {
            "code": 200,
            "data": genres
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)