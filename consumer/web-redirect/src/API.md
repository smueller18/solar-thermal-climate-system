# API - SocketIO

## Connection events
A list of events which are send after establishing connection. 

### `sensor_values_cache`
After a client connected, this event is used to push all latest available messages. For each topic, a separate message is send. The structure of the messages are as follows:
```json
{
  "topic": <topic>,
  "timestamp": <timestamp>,
  "data": {
    "sensorId1": <value>,
    "sensorId2": <value>,
    ...
  }
}
```

## Broadcast events
A list of broadcast events which are send to every connected client.
### `sensor_values`
This event is pushed as soon as a new Kafka message arrives. The structure of the messages are as follows:
```json
{
  "topic": <topic>,
  "timestamp": <timestamp>,
  "data": {
    "sensorId1": <value>,
    "sensorId2": <value>,
    ...
  }
}
```

### `connected_clients`
This is a broadcast event which is send to all connected clients as soon as a new Kafka message arrives. The structure of the  messages are as follows:
```json
<number_of_connected_clients>
```
