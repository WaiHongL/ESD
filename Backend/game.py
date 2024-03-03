from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:password@luden-user.cbki4scc2nyk.ap-southeast-1.rds.amazonaws.com/game'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Game(db.Model):
    __tablename__ = 'game'

    title = db.Column(db.String(255), primary_key=True)
    genre = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)

    def __init__(self, title, genre, price):
        self.title = title
        self.genre = genre
        self.price = price

    def json(self):
        return {
            "title": self.title,
            "genre": self.genre,
            "price": self.price
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

# GET GAME GENRES
@app.route("/games/genre", methods=["POST"])
def get_games_genre():
    cart_data = request.get_json()['data']['cart']
    purchase_data = request.get_json()['data']['purchase']
    
    # CONCATENATE cart_data and purchase_data
    data_arr = cart_data + purchase_data
    titles = []

    for data in data_arr:
        for key, value in data.items():
            if key == "game_title" and value not in titles:
                titles.append(value)

    # GET GENRES
    genres = []
    for title in titles:
        game = db.session.scalars(db.select(Game).filter_by(title=title).limit(1)).first()
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