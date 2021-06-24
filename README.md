# Data Streaming System with Kafka and ClickHouse

## Run Kafka, ClickHouse and other services in the tutorial

```bash
$ sudo docker-compose up
```

## Create a Kafka topic

```bash
$ sudo docker exec -it kafka-broker kafka-topics \
--zookeeper 192.168.1.40:2181 \
--create \
--topic readings \
--partitions 4 \
--replication-factor 1
```

## Configure ClickHouse to receive data from Kafka

![Structure](https://altinity.com/wp-content/uploads/2020/07/Screenshotfrom2020-05-1420-53-15.png)

### Open ClickHouse CLI

```bash
$ sudo docker exec -it clickhouse bin/bash -c "clickhouse-client --multiline"
```

1. Create a MergeTree Table

```bash
CREATE TABLE readings (
    readings_id Int32 Codec(DoubleDelta, LZ4),
    time DateTime Codec(DoubleDelta, LZ4),
    date ALIAS toDate(time),
    temperature Decimal(5,2) Codec(T64, LZ4)
) Engine = MergeTree
PARTITION BY toYYYYMM(time)
ORDER BY (readings_id, time);
```

2. Create Kafka Table Engine

```bash
CREATE TABLE readings_queue (
    readings_id Int32,
    time DateTime,
    temperature Decimal(5,2)
)
ENGINE = Kafka
SETTINGS kafka_broker_list = '192.168.1.40:9091',
       kafka_topic_list = 'readings',
       kafka_group_name = 'readings_consumer_group1',
       kafka_format = 'CSV',
       kafka_max_block_size = 1048576;
```

3. Create a materialized view to transfer data between Kafka and the merge tree table

```bash
CREATE MATERIALIZED VIEW readings_queue_mv TO readings AS
SELECT readings_id, time, temperature
FROM readings_queue;
```

4. Test the setup by producing some messages

```bash
sudo docker exec -it kafka-broker kafka-console-producer \
--broker-list 192.168.1.40:9091 \
--topic readings

# Data
1,"2020-05-16 23:55:44",14.2
2,"2020-05-16 23:55:45",20.1
3,"2020-05-16 23:55:51",12.9
```

## Configure ClickHouse on Superset

1. Register a root ClickHouse account

```bash
$ sudo docker exec -it superset superset-init
```

2. Connect to ClickHouse

- Use the UI at localhost:8080
- Add Clickhouse URI to Superset: clickhouse://clickhouse:8123

## Source

https://altinity.com/blog/2020/5/21/clickhouse-kafka-engine-tutorial
