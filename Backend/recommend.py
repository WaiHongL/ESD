from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

# Initialize flasgger for API Documentation
app.config['SWAGGER'] = {
    'title': 'Recommend microservice API',
    'version': 2.0,
    "openapi": "3.0.2",
    'description': 'Recommends games to users based on aggregation and comparison of genres',
    'tags': {
        'Recommend': 'Operations related to recommendation of games',
    },    
}

swagger = Swagger(app) 
   
# GET COMMON GENRE
@app.route("/recommend/genre", methods=["POST"])
def get_common_genre():
    """
    Recommends game genres to user
    ---
    tags:
        - ['Recommend']
    requestBody:
        required: true
        content:
            application/json:
                schema:
                    type: object
                    properties:
                        data:
                            type: array
                            items:
                                type: string
                                description: Game genre
    responses:
        200:
            description: Most common genre returned successfully
        400:
            description: Invalid JSON input
        404:
            description: No common genres found
    """
    if request.get_json():
        genre_data = request.get_json()
        genre_dict = {}

        for genre in genre_data:
            if genre not in genre_dict:
                genre_dict[genre] = 1
            else:
                genre_dict[genre] += 1

        # CHECKS IF ALL GENRES ONLY HAVE ONE COUNT
        is_one_count = True
        for genre, count in genre_dict.items():
            if count > 1:
                is_one_count = False

        if is_one_count:
            return jsonify(
                {
                    "code": 200,
                    "data": genre_data
                }
            )

        # CHECKS IF GENRE_DATA IS EMPTY
        try:
            max_value = max(genre_dict.values())

            common_genre = [k for k,v in genre_dict.items() if v == max_value]
            #common_genre = max(genre_dict, key=genre_dict.get)
            return jsonify(
                {
                    "code": 200,
                    "data": common_genre
                }
            )
        except Exception as e:
            return jsonify(
                {
                    "code": 404,
                    "data": "There are no common genres."
                }
            )    
                
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5602, debug=True)