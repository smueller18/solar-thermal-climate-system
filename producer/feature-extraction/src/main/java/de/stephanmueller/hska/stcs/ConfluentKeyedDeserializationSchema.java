/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import io.confluent.kafka.serializers.KafkaAvroDecoder;
import kafka.utils.VerifiableProperties;
import org.apache.avro.generic.GenericRecord;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.typeutils.TypeExtractor;
import org.apache.flink.streaming.util.serialization.KeyedDeserializationSchema;

import java.io.IOException;
import java.util.Properties;


public class ConfluentKeyedDeserializationSchema implements KeyedDeserializationSchema<GenericKeyValueRecord> {

    private static KafkaAvroDecoder decoder;


    public ConfluentKeyedDeserializationSchema(String schemaRegistryUrl) {

        if(decoder == null) {
            Properties props = new Properties();
            props.put("schema.registry.url", schemaRegistryUrl);
            VerifiableProperties vProps = new VerifiableProperties(props);

            decoder = new KafkaAvroDecoder(vProps);
        }
    }

    @Override
    public GenericKeyValueRecord deserialize(byte[] messageKey, byte[] message, String topic, int partition, long offset)
            throws IOException {

        return new GenericKeyValueRecord(
                (GenericRecord) decoder.fromBytes(messageKey),
                (GenericRecord) decoder.fromBytes(message)
        );
    }

    @Override
    public boolean isEndOfStream(GenericKeyValueRecord genericKeyValueRecord) {
        return false;
    }

    @Override
    public TypeInformation<GenericKeyValueRecord> getProducedType() {
        return TypeExtractor.getForClass(GenericKeyValueRecord.class);
    }
}