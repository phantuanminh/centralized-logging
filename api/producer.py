from kafka import KafkaProducer
from time import sleep

# Initiate Producer
producer = KafkaProducer(
    bootstrap_servers=['192.168.1.40:9091'], security_protocol='PLAINTEXT')
# Asynchronous by default
# future = producer.send(topic='my-topic', value=b'raw_bytes')
producer.send(topic='test',
              partition=0, value=b'asdasd')
sleep(0.5)
producer.close()
