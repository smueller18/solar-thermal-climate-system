# Kafka

## Delete topics
1. Set `KAFKA_DELETE_TOPIC_ENABLE=True`in config.env
2. Stop all containers and only start Kafka and Zookeeper
3. Run command:
```
docker-compose exec kafka /bin/sh /opt/kafka_2.10-0.9.0.0/bin/kafka-topics.sh --zookeeper zookeeper:2181 --delete --topic <topic>
```
