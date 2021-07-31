from clickhouse_driver import Client

client = Client(host='clickhouse', port='8123')
client.execute('SELECT * FROM system.numbers LIMIT 5')
client.execute('SHOW DATABASES')
client.disconnect()