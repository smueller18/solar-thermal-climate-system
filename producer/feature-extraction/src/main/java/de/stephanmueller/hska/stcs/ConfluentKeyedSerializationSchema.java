/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import kafka.serializer.Encoder;
import kafka.utils.VerifiableProperties;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;
import org.apache.flink.streaming.util.serialization.KeyedSerializationSchema;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.logging.Logger;


public class ConfluentKeyedSerializationSchema implements KeyedSerializationSchema<KeyValuePair> {

    private static final Logger log = Logger.getLogger(ConfluentKeyedSerializationSchema.class.getName());

    private String schemaRegistryUrl;
    private String keySchemaRessource;
    private String valueSchemaRessource;
    private String topic;

    private transient Schema keySchema;
    private transient Schema valueSchema;
    private transient Encoder keyEncoder;
    private transient Encoder valueEncoder;


    public ConfluentKeyedSerializationSchema(String schemaRegistryUrl, String keySchemaRessource, String valueSchemaRessource, String topic)
            throws IOException {

        this.schemaRegistryUrl = schemaRegistryUrl;
        this.keySchemaRessource = keySchemaRessource;
        this.valueSchemaRessource = valueSchemaRessource;
        this.topic = topic;

    }

    @Override
    public byte[] serializeKey(KeyValuePair keyValuePair) {

        if (this.keySchema == null) {

            Schema.Parser parser = new Schema.Parser();
            try {
                this.keySchema = parser.parse(FeatureExtraction.class.getResourceAsStream(keySchemaRessource));
            } catch (IOException e) {
            }

            Properties props = new Properties();
            props.put("schema.registry.url", this.schemaRegistryUrl);
            VerifiableProperties vProps = new VerifiableProperties(props);

            this.keyEncoder = new KafkaAvroKeyEncoder(this.topic, vProps);
        }

        GenericRecord record = new GenericData.Record(this.keySchema);

        for (String key : keyValuePair.getKeys().keySet()) {
            record.put(key, keyValuePair.getKey(key));
        }

        return ((KafkaAvroKeyEncoder) this.keyEncoder).toBytes(record);

    }

    @Override
    public byte[] serializeValue(KeyValuePair keyValuePair) {

        if (this.valueSchema == null) {

            Schema.Parser parser = new Schema.Parser();
            try {
                this.valueSchema = parser.parse(FeatureExtraction.class.getResourceAsStream(valueSchemaRessource));
            } catch (IOException e) {
            }

            Properties props = new Properties();
            props.put("schema.registry.url", this.schemaRegistryUrl);
            VerifiableProperties vProps = new VerifiableProperties(props);

            this.valueEncoder = new KafkaAvroValueEncoder(this.topic, vProps);
        }

        GenericRecord record = new GenericData.Record(this.valueSchema);

        for (String key : keyValuePair.getValues().keySet()) {
            record.put(key, keyValuePair.getValue(key));
        }

        return ((KafkaAvroValueEncoder) this.valueEncoder).toBytes(record);

    }

    @Override
    public String getTargetTopic(KeyValuePair element) {
        return null;
    }

}