from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)

# Enable Cross-Origin Requests
CORS(app)

# Routing Management
@app.route('/api/', methods=['POST'])
@cross_origin(supports_credentials=True)
def sign_up():
    return jsonify({'result': 'fail'})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
