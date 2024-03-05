from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/check-time', methods=['GET'])
def check_time():
    # Extract gameplay time from query parameters
    gameplay_time = request.args.get('gameplayTime', default=0, type=int)
    
    # Check if gameplay time is less than 2 hours (120 minutes)
    if gameplay_time < 120:
        return jsonify({"eligibleForRefund": True})
    else:
        return jsonify({"eligibleForRefund": False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
