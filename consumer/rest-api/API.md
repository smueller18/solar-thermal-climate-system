# API - Cache REST

## Resources
###[`/topics`](topics)
Returns most recent sensor data for all available topics. The structure of the responses is as follows:
```json
{
  "<topic1>": {
    "timestamp": <timestamp>,
    "data": {
      "sensorId1": <value>,
      "sensorId2": <value>,
      ...
    }  
  },
  ...
}
```

###[`/topic/<topic>`](topic/<topic>)
Returns most recent sensor data for the selected topic. The structure of the responses is as follows:
```json
{
  "timestamp": <timestamp>,
  "topic": "<topic>",
  "data": {
    "sensorId1": <value>,
    "sensorId2": <value>,
    ...
  }
}
```

## Errors
If an error occurred, an error message is send as follows:
```json
{
  "error": "<error>"
}
```