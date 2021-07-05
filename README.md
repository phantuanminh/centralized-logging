# Centralized Logging System for Docker Containers

## I. General Structure

```
            Mechanism        Mechanism            Mechanism
                A                B                    C
                |                |                    |
> Service 1 --------  Zookeeper  |                    |
                    \    &       |                    |
> Service 2 ---------> Kafka --------> ClickHouse -------> Superset
                    /(Rsyslog)
> Service n --------

```

Notes:

- Each service represents a Docker Container.
- Zookeeper is a MUST for Kafka. [Why?](https://stackoverflow.com/questions/23751708/is-zookeeper-a-must-for-kafka)
- To save space, we can try to run Zookeeper, Kafka, ClickHouse, Superset in a single container.

## II. Framework / Services Introduction

> Let's have a brief introduction about some of the framework we might be using, and why they could possibly help.

- [Kafka](https://kafka.apache.org/):
  - Kafka is an open source software which provides a framework for storing, reading and analysing streaming data.
  - We can use Kafka to distribute log messages from multiple services.
  - Multiple Kafka nodes should be used in deployment, and Zookeeper is mandatory to help manage Kafka nodes. Read more about Zookeeper here: https://zookeeper.apache.org/
- [ClickHouse](https://clickhouse.tech/)
  - ClickHouse is a fast open-source OLAP database management system.
  - We can benefit from ClickHouse Kafka Engine (which helps to connect with Kafka) and ClickHouse connection with Superset.
- [Superset](https://superset.apache.org/)
  - For visualizing data.

## III. Mechanism Discussion

<b>1. Mechanism A:</b> Transmits all logging messages from multiple services (Docker Containers) to Kafka.

- First, we need to figure out how Docker handle its logging -> [Docker Logging Driver](https://docs.docker.com/config/containers/logging/configure/).
- I propose 3 possible solutions:
  - [Moby Kafka Logdriver](https://github.com/MickayG/moby-kafka-logdriver): A Docker plugin that works as a logdriver, transmit all log messages to Kafka.
  - Rsyslog: Transmit all log messages to a rsyslog server, then rsyslog decides where the messages go. [Rsyslog Project For Kafka](https://github.com/JPvRiel/docker-rsyslog)
  - Other ways than Moby to configure a custom logging mechanism for all services, each service would work like a producer.

<b>2. Mechanism B:</b> Configure ClickHouse to automatically receive data from Kafka.

> Check out this really helpful tutorial: [Link](https://altinity.com/blog/2020/5/21/clickhouse-kafka-engine-tutorial)

![Structure](https://altinity.com/wp-content/uploads/2020/07/Screenshotfrom2020-05-1420-53-15.png)

<b>3. Mechanism C:</b> Configure Superset to visualize ClickHouse data

- Setup Superset User Interface. Use the interface to connect to ClickHouse URI -> Then it's all done!

## IV. Demo

> In order to properly test Mechanism A, we should have already setted up and test Mechanism B and C, so let's set up the latter part first.

<b> 1. Mechanism B </b>

- Run Kafka & Zookeeper, ClickHouse, Superset:

  ```bash
  $ sudo docker-compose up -d
  ```

- Init a variable as your machine IP address:

  ```bash
  $ IP_ADDRESS = {YOUR_MACHINE_IP_ADDRESS}
  ```

  ```bash
  $ sudo docker exec -it kafka-broker kafka-topics \
  --zookeeper $IP_ADDRESS:2181 \
  --create \
  --topic readings \
  --partitions 6 \
  --replication-factor 1
  ```

- Check if the topic is created or not:

  ```bash
  $ sudo docker exec -it kafka-broker kafka-topics \
  --zookeeper $IP_ADDRESS:2181 \
  --describe readings
  ```

- Configure ClickHouse to receive data from Kafka

  ![Structure](https://altinity.com/wp-content/uploads/2020/07/Screenshotfrom2020-05-1420-53-15.png)

- Open ClickHouse CLI

  ```bash
  $ sudo docker exec -it clickhouse bin/bash -c "clickhouse-client --multiline"
  ```

  ```bash
  # Create a MergeTree Table
  CREATE TABLE readings (
      readings_id Int32 Codec(DoubleDelta, LZ4),
      time DateTime Codec(DoubleDelta, LZ4),
      date ALIAS toDate(time),
      temperature Decimal(5,2) Codec(T64, LZ4)
  ) Engine = MergeTree
  PARTITION BY toYYYYMM(time)
  ORDER BY (readings_id, time);
  ```

  ```bash
  # Create Kafka Table Engine
  CREATE TABLE readings_queue (
      readings_id Int32,
      time DateTime,
      temperature Decimal(5,2)
  )
  ENGINE = Kafka
  SETTINGS kafka_broker_list = '{YOUR_MACHINE_IP_ADDRESS}:9091',
      kafka_topic_list = 'readings',
      kafka_group_name = 'readings_consumer_group1',
      kafka_format = 'CSV',
      kafka_max_block_size = 1048576;
  ```

  ```bash
  # Create a materialized view to transfer data
  # between Kafka and the merge tree table
  CREATE MATERIALIZED VIEW readings_queue_mv TO readings AS
  SELECT readings_id, time, temperature
  FROM readings_queue;
  ```

- Test the setup by producing some messages

  ```bash
  sudo docker exec -it kafka-broker kafka-console-producer \
  --broker-list {YOUR_MACHINE_IP_ADDRESS}:9091 \
  --topic readings
  ```

  ```
  # Data
  1,"2020-05-16 23:55:44",14.2
  2,"2020-05-16 23:55:45",20.1
  3,"2020-05-16 23:55:51",12.9
  ```

<b> 2. Mechanism C </b>

1. Register a root ClickHouse account

   ```bash
   $ sudo docker exec -it superset superset-init
   ```

2. Connect to ClickHouse

   - Use the UI at localhost:8080
   - Add Clickhouse URI to Superset: clickhouse://clickhouse:8123
   - Then you should be able to visualize some ClickHouse Tables

## Reference

- https://altinity.com/blog/2020/5/21/clickhouse-kafka-engine-tutorial
