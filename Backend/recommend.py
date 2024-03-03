from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
    
# GET COMMON GENRE
@app.route("/recommend/genre", methods=["POST"])
def get_common_genre():
    genre_data = request.get_json()["data"]
    genre_dict = {}

    for genre in genre_data:
        if genre not in genre_dict:
            genre_dict[genre] = 1
        else:
            genre_dict[genre] += 1

    common_genre = max(genre_dict, key=genre_dict.get)

    return jsonify(
        {
            "code": 200,
            "data": common_genre
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5300, debug=True)