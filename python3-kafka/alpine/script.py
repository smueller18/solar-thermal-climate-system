from pykafka import KafkaClient
import time

client = KafkaClient(hosts="kafka:9092", socket_timeout_ms=100)
topic = client.topics[str.encode("test")]

producer = topic.get_producer(use_rdkafka=True, sync=True)
i = 0

while True:
    producer.produce(str.encode(str(i)))
    i += 1
    print(i)
    time.sleep(1)
