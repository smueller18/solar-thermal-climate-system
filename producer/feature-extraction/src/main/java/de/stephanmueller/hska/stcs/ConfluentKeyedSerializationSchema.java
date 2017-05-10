/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import kafka.utils.VerifiableProperties;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;
import kafka.serializer.Encoder;
import org.apache.flink.streaming.util.serialization.KeyedSerializationSchema;

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Properties;
import java.util.logging.Logger;


public class ConfluentKeyedSerializationSchema implements KeyedSerializationSchema<KeyValuePair> {

    private static final Logger log = Logger.getLogger(ConfluentKeyedSerializationSchema.class.getName());

    private static HashMap<String, Schema> schemaHash = new HashMap<>();
    private static HashMap<String, Encoder> encoderHash = new HashMap<>();

    private String keySubject;
    private String valueSubject;


    public ConfluentKeyedSerializationSchema(String schemaRegistryUrl, InputStream keySchemaStream, InputStream valueSchemaStream, String topic)
            throws IOException {

        this.keySubject = topic + "-key";
        this.valueSubject = topic + "-value";

        Schema.Parser parser = new Schema.Parser();
        schemaHash.put(this.keySubject, parser.parse(keySchemaStream));
        schemaHash.put(this.valueSubject, parser.parse(valueSchemaStream));

        Properties props = new Properties();
        props.put("schema.registry.url", schemaRegistryUrl);
        VerifiableProperties vProps = new VerifiableProperties(props);

        if (!encoderHash.containsKey(this.keySubject))
            encoderHash.put(this.keySubject, new KafkaAvroKeyEncoder(topic, vProps));

        if (!encoderHash.containsKey(this.valueSubject))
            encoderHash.put(this.valueSubject, new KafkaAvroValueEncoder(topic, vProps));
    }

    @Override
    public byte[] serializeKey(KeyValuePair keyValuePair) {

        GenericRecord record = new GenericData.Record(schemaHash.get(this.keySubject));

        for (String key : keyValuePair.getKeys().keySet()) {
            record.put(key, keyValuePair.getKey(key));
        }

        return ((KafkaAvroKeyEncoder) encoderHash.get(this.keySubject)).toBytes(record);
    }

    @Override
    public byte[] serializeValue(KeyValuePair keyValuePair) {

        GenericRecord record = new GenericData.Record(schemaHash.get(this.valueSubject));

        for (String key : keyValuePair.getValues().keySet()) {
            record.put(key, keyValuePair.getValue(key));
        }

        return ((KafkaAvroValueEncoder) encoderHash.get(this.valueSubject)).toBytes(record);
    }

    @Override
    public String getTargetTopic(KeyValuePair element) {
        return null;
    }

}