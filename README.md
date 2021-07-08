# Centralized Logging System for Docker Containers

## I. General Structure

> So what are we trying to build?

- We want to design a system that can automatically store and handle the logs from multiple services.

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
  - Kafka is an open source software which provides a framework for storing, reading and analysing streaming data. Simply speaking, Kafka works like a messaging queue, but distributedly.
  - We can use Kafka to distribute log messages from multiple services. 3 Kafka main components: producers, consumers, brokers (nodes). Kafka messages are distributed under a "topic". Read more on Kafka website.
  - Multiple Kafka nodes should be used in deployment, and Zookeeper is mandatory to help manage Kafka nodes. Read more about Zookeeper here: https://zookeeper.apache.org/
- [ClickHouse](https://clickhouse.tech/)
  - ClickHouse is a fast open-source OLAP database management system.
  - We can benefit from ClickHouse Kafka Engine (which helps to connect with Kafka) and ClickHouse connection with Superset.
- [Superset](https://superset.apache.org/)
  - Able to connect to ClickHouse and visualize data.

## III. Mechanism Discussion

<b>1. Mechanism A:</b> Transmits all logging messages from multiple services (Docker Containers) to Kafka.

- First, we need to figure out how Docker handle its logging -> [Docker Logging Driver](https://docs.docker.com/config/containers/logging/configure/).
- I propose 3 possible solutions:
  - [Moby Kafka Logdriver](https://github.com/MickayG/moby-kafka-logdriver): A Docker plugin that works as a logdriver, transmit all log messages to Kafka.
  - Rsyslog: Transmit all log messages to a rsyslog server, then rsyslog decides where the messages go. [Rsyslog Project For Kafka](https://github.com/JPvRiel/docker-rsyslog)
  - Other ways than Moby to configure a custom logging mechanism for all services, and then some way to produce log messages to Kafka.

<b>2. Mechanism B:</b> Configure ClickHouse to automatically receive data from Kafka.

> Check out this really helpful tutorial: [Link](https://altinity.com/blog/2020/5/21/clickhouse-kafka-engine-tutorial)

![Structure](https://altinity.com/wp-content/uploads/2020/07/Screenshotfrom2020-05-1420-53-15.png)

- Note: We can configure each table to receive messages from Kafka topics (They are basically Kafka consumers).

<b>3. Mechanism C:</b> Configure Superset to visualize ClickHouse data

- Setup Superset User Interface. Use the interface to connect to ClickHouse URI -> Then it's all done!

## IV. Full Solution Demo

We will test exploration with a full demo that handles the logs of 3 seperate services.

Note: You will need to edit the IP address in this file and inside docker-compose.yml to match you machine's.

> Let's follow the design below

```
              Kafka             Kafka
            Log Driver      Table Engine
                |                |
> Service 1 --------  Zookeeper  |
                    \    &       |
> Service 2 ---------> Kafka --------> ClickHouse -------> Superset
                    /(Rsyslog)
> Service n --------

```

<b> Start the demo by running our base services </b>

- Run Kafka & Zookeeper, ClickHouse, Superset: Remember to edit docker-compose.yml to fit your machine settings.

```bash
$ sudo docker-compose up -d
```

- Init a variable as your machine IP address:

```bash
$ IP_ADDRESS={YOUR_MACHINE_IP_ADDRESS}
```

- Create 3 topics:

```bash
$ sudo docker exec -it kafka-broker kafka-topics \
--zookeeper $IP_ADDRESS:2181 \
--create \
--topic service_1 \
--partitions 6 \
--replication-factor 1
```

```bash
$ sudo docker exec -it kafka-broker kafka-topics \
--zookeeper $IP_ADDRESS:2181 \
--create \
--topic service_2 \
--partitions 6 \
--replication-factor 1
```

```bash
$ sudo docker exec -it kafka-broker kafka-topics \
--zookeeper $IP_ADDRESS:2181 \
--create \
--topic service_3 \
--partitions 6 \
--replication-factor 1
```

- Check if the topic is created or not:

```bash
$ sudo docker exec -it kafka-broker kafka-topics \
--zookeeper $IP_ADDRESS:2181 \
--describe
```

<b>1. Start 3 services that always generate logs and send to Kafka using Kafka Log Driver</b>

First, we need to install and configure Kafka Log Driver, we will need 3 seperate plugins for 3 services.

- Set a local name for each plugin.
- Disable to configure them first before running.
- More detailed guide: https://github.com/MickayG/moby-kafka-logdriver

```bash
$ sudo docker plugin install --alias service_1_logdriver --disable mickyg/kafka-logdriver:latest
$ sudo docker plugin set service_1_logdriver KAFKA_BROKER_ADDR="192.168.1.40:9091"
$ sudo docker plugin set service_1_logdriver LOG_TOPIC=service_1
$ sudo docker plugin enable service_1_logdriver:latest
```

```bash
$ sudo docker plugin install --alias service_2_logdriver --disable mickyg/kafka-logdriver:latest
$ sudo docker plugin set service_2_logdriver KAFKA_BROKER_ADDR="192.168.1.40:9091"
$ sudo docker plugin set service_2_logdriver LOG_TOPIC=service_2
$ sudo docker plugin enable service_2_logdriver
```

```bash
$ sudo docker plugin install --alias service_3_logdriver --disable mickyg/kafka-logdriver:latest
$ sudo docker plugin set service_3_logdriver KAFKA_BROKER_ADDR="192.168.1.40:9091"
$ sudo docker plugin set service_3_logdriver LOG_TOPIC=service_3
$ sudo docker plugin enable service_3_logdriver
```

Build our random logger images:

```bash
$ sudo docker build -t random-logger_1 ./random-logger
$ sudo docker build -t random-logger_2 ./random-logger
$ sudo docker build -t random-logger_3 ./random-logger
```

Run 3 services with configured log drivers:

```bash
$ sudo docker run --detach --log-driver service_1_logdriver random-logger_1
$ sudo docker run --detach --log-driver service_2_logdriver random-logger_2
$ sudo docker run --detach --log-driver service_3_logdriver random-logger_3
```

Make sure that Kafka is receiving the log messages by creating a consumer that is subscribed to each topic. The message should be appearing on the command line window. Later on, ClickHouse will be our Kafka Consumer.

```bash
$ sudo docker exec -it kafka-broker kafka-console-consumer --bootstrap-server 192.168.1.40:9091 --topic service_1
```

<b> 2. Configure ClickHouse as a Kafka Consumer </b>

- Configure ClickHouse to receive data from Kafka

  ![Structure](https://altinity.com/wp-content/uploads/2020/07/Screenshotfrom2020-05-1420-53-15.png)

- Let's design the ClickHouse data tables based on our logging messages, which is a <b>one row nested JSON format</b>. I will work with the first layer of JSON only, the nested part need to be handled later on.

```
{"Line":"{"@timestamp": "2021-07-08T10:44:08+0000", "level": "WARN", "message": "variable not in use."}","Source":"stdout","Timestamp":"2021-07-08T10:44:08.349998689Z","Partial":false,"ContainerName":"/cool_shamir","ContainerId":"4e07abaf3345e8d8b026826c49d3193e401e2635781dae86cbd57ec9579d18c1","ContainerImageName":"random-logger","ContainerImageId":"sha256:cbc554adcaabd8ce581d438a2223d2ebae3ccb84d477867b63bdfb4b91632067","Err":null}
```

- Let's split this up for a better look:

```json
{
  "Line":"{"@timestamp": "2021-07-08T10:44:08+0000", "level": "WARN", "message": "variable not in use."}",
  "Source":"stdout",
  "Timestamp":"2021-07-08T10:44:08.349998689Z",
  "Partial":false,
  "ContainerName":"/cool_shamir",
  "ContainerId":"4e07abaf3345e8d8b026826c49d3193e401e2635781dae86cbd57ec9579d18c1",
  "ContainerImageName":"random-logger",
  "ContainerImageId":"sha256:cbc554adcaabd8ce581d438a2223d2ebae3ccb84d477867b63bdfb4b91632067",
  "Err":null
}
```

- Open ClickHouse CLI

```bash
$ sudo docker exec -it clickhouse bin/bash -c "clickhouse-client --multiline"
```

<b> Important: Repeat this design for each service, below is a demo for service_1 </b>

```bash
# Create a MergeTree Table
CREATE TABLE service_1 (
    line String,
    source String,
    timestamp DateTime Codec(DoubleDelta, LZ4)
) Engine = MergeTree
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp);
```

```bash
# Create Kafka Table Engine
CREATE TABLE service_1_queue (
    line String,
    source String,
    timestamp DateTime Codec(DoubleDelta, LZ4)
)
ENGINE = Kafka
SETTINGS kafka_broker_list = '192.168.1.40:9091',
    kafka_topic_list = 'service_1',
    kafka_group_name = 'service_1_consumer_1',
    kafka_format = 'JSONEachRow',
    kafka_max_block_size = 1048576;
```

```bash
# Create a materialized view to transfer data
# between Kafka and the merge tree table
CREATE MATERIALIZED VIEW service_1_queue_mv TO service_1 AS
SELECT line, source, timestamp
FROM service_1_queue;
```

- (Optional because the services has been producing messages already) Test the setup by producing some messages

  ```bash
  sudo docker exec -it kafka-broker kafka-console-producer \
  --broker-list 192.168.1.40:9091 \
  --topic readings
  ```

- Use this data

  ```
  {"Line":"{\"@timestamp\": \"2021-07-08T10:44:08+0000\", \"level\": \"WARN\", \"message\": \"variable not in use.\"}","Source":"stdout","Timestamp":"2021-07-08T10:44:08.349998689Z","Partial":false,"ContainerName":"/cool_shamir","ContainerId":"4e07abaf3345e8d8b026826c49d3193e401e2635781dae86cbd57ec9579d18c1","ContainerImageName":"random-logger","ContainerImageId":"sha256:cbc554adcaabd8ce581d438a2223d2ebae3ccb84d477867b63bdfb4b91632067","Err":null}
  ```

<b> 3. Configure SuperSet to get data from ClickHouse </b>

1. Register a root SuperSet account

   ```bash
   $ sudo docker exec -it superset superset-init
   ```

2. Connect to ClickHouse

   - Use the UI at localhost:8080
   - Add Clickhouse URI to Superset: clickhouse://clickhouse:8123
   - Then you should be able to visualize some ClickHouse Tables

## Reference

- https://altinity.com/blog/2020/5/21/clickhouse-kafka-engine-tutorial
