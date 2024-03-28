from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app, supports_credentials=True)

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

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:pSSSS+]q8zZ-pjF:@34.142.233.183/shop'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Game(db.Model):
    __tablename__ = 'game'

    game_id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    points = db.Column(db.Integer, nullable=False)

    def __init__(self, title, genre, price, points):
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

class Customizations(db.Model):
    __tablename__ = 'customizations'

    customization_id = db.Column(db.Integer, primary_key=True)
    tier = db.Column(db.String(255), nullable=False)
    border_color = db.Column(db.String(255), nullable=False)
    credits = db.Column(db.Integer, nullable=False)

    def __init__(self, tier, border_color, credits):
        self.tier = tier
        self.border_color = border_color
        self.credits = credits

    def json(self):
        return {
            "customization_id": self.customization_id,
            "tier": self.tier,
            "border_color": self.border_color,
            "credits": self.credits
        }
    
# GET ALL GAMES AND GAMES BY GENRE
@app.route("/games")
def get_games():
    """
    Get all games
    ---
    tags:
        - ['Games']  
    responses:
        200:
            description: Returned game details successfully
        404:
            description: Games not found
    """
    # CHECK IF "GENRE" IS IN QUERY PARAMS
    if (request.args.get("genre")):
        genre = request.args.get("genre")

        try:
            gameList = db.session.scalars(db.select(Game).filter_by(genre=genre)).all()

            if len(gameList):
                return jsonify(
                    {
                        "code": 200,
                        "data": {
                            "games": [game.json() for game in gameList]
                        }
                    }
                ), 200

            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "genre": genre
                    },
                    "message": "There are no games that matches the genre"
                }
            ), 404
        
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "genre": genre
                    },
                    "message": "An error occurred while getting games that matches the genre"
                }
            ), 500
    
    # FOR FRONTEND
    try:
        gameList = db.session.scalars(db.select(Game)).all()

        if len(gameList):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "games": [game.json() for game in gameList]
                    }
                }
            ), 200
        
        return jsonify(
            {
                "code": 404,
                "message": "There are no games"
            }
        ), 404
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while getting games"
            }
        ), 500


# GET GAME GENRES
@app.route("/games/genre", methods=["POST"])
def get_games_genre():
    """
    Get games genres
    ---
    tags:
        - ['Games']  
    requestBody:
        description: Games Genre 
        required: true
        content:
            application/json:
                schema:
                    properties:
                        game_id: 
                            type: integer
                            description: Game ID
                        customization_id: 
                            type: integer
                            description: Customization ID
    responses:
        200:
            description: Returned game genres successfully
        404:
            description: Game genres not found
    """
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
                if (key == "game_id" or key == "customization_id") and value not in games_id_arr:
                    games_id_arr.append(value)

        # GET GENRES
        genres = []
        for game_id in games_id_arr:
            game = db.session.scalars(db.select(Game).filter_by(game_id=game_id).limit(1)).first()
            if game:
                genre = game.genre
                genres.append(genre)

        if len(genres) > 0:
            return jsonify(
                {
                    "code": 200,
                    "data": genres
                }
            ), 200
        else:
            return jsonify(
                {
                    "code": 404,
                    "data": "There are no game genres"
                }
            ), 404
        
    return jsonify(
        {
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }
    ), 400


# GET GAME DETAILS
@app.route("/games/<int:gameId>")
def get_game_details(gameId):
    """
    Get games genres
    ---
    parameters:
        -   in: path
            name: gameId
            required: true 
    tags:
        - ['Games']  
    responses:
        200:
            description: Return game details
        404:
            description: Game details not found
    """
    try:
        game = db.session.scalars(db.select(Game).filter_by(game_id=gameId)).one()
        if (game):
            # print(game)
            return jsonify(
                {
                    "code": 200,
                    "data": game.json()
                }
            ), 200
        
        return jsonify(
            {
                "code": 404,
                "data": {
                    "game_id": gameId
                },
                "message": "Game does not exist"
            }
        ), 404
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "game_id": gameId
                },
                "message": "An error occurred while getting game details"
            }
        ), 500


# GET ALL CUSTOMIZATIONS
@app.route("/customizations")
def get_customizations():
    """
    Get all customizations
    ---
    tags:
        - ['Customizations']  
    responses:
        200:
            description: Returned customizations successfully
        404:
            description: Games not found
    """
    try: 
        customization_list = db.session.scalars(db.select(Customizations)).all()

        if len(customization_list):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "customizations": [customization.json() for customization in customization_list]
                    }
                }
            ), 200
        
        return jsonify(
            {
                "code": 404,
                "message": "There are no customizations"
            }
        ), 404
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while getting customizations"
            }
        ), 500


# GET CUSTOMIZATION DETAILS
@app.route("/customizations/<int:customizationId>")
def get_customization_details(customizationId):
    """
    Get customization details
    ---
    parameters:
        -   in: path
            name: customizationId
            required: true 
    tags:
        - ['Customizations']  
    responses:
        200:
            description: Returned customization details successfully
        404:
            description: Games not found
    """
    try: 
        customization = db.session.scalars(db.select(Customizations).filter_by(customization_id=customizationId)).one()

        if customization:
            return jsonify(
                {
                    "code": 200,
                    "data": customization.json()
                }
            ), 200
        
        return jsonify(
            {
                "code": 404,
                "data": {
                    "customization_id": customizationId
                },
                "message": "Customization does not exist"
            }
        ), 404
    
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "customization_id": customizationId
                },
                "message": "An error occurred while getting customization details"
            }
        ), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)