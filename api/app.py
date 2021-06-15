from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)

# Enable Cross-Origin Requests
CORS(app, supports_credentials=True)


@app.route('/api/message', methods=['POST', 'GET', 'OPTIONS'])
def message():
    data = request.get_json()
    return jsonify({'result': 'fail'})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
