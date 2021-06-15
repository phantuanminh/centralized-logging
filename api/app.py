from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from kafka import KafkaProducer
from time import sleep

app = Flask(__name__)

# Enable Cross-Origin Requests
CORS(app, supports_credentials=True)


@app.route('/api/message', methods=['POST', 'GET', 'OPTIONS'])
def message():
    # Get data from request
    data = request.get_json()

    # Initiate Producer
    producer = KafkaProducer(bootstrap_servers=['192.168.1.40:9091'])
    producer.send(topic=data['topic'],
                  partition=data['partition'], value=data['message'].tobytes())
    sleep(0.5)

    return jsonify({'result': 'fail'})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
