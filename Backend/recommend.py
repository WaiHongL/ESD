from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
    
# GET COMMON GENRE
@app.route("/recommend/genre", methods=["POST"])
def get_common_genre():
    if request.get_json():
        genre_data = request.get_json()["data"]
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
            common_genre = max(genre_dict, key=genre_dict.get)
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
    app.run(host='0.0.0.0', port=5300, debug=True)