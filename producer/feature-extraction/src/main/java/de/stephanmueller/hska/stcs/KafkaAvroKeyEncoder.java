/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import io.confluent.kafka.serializers.AbstractKafkaAvroSerializer;
import kafka.serializer.Encoder;
import kafka.utils.VerifiableProperties;

public class KafkaAvroKeyEncoder extends AbstractKafkaAvroSerializer implements Encoder<Object> {

    private String topic;

    public KafkaAvroKeyEncoder(String topic, VerifiableProperties props) {
        this.topic = topic;
        configure(serializerConfig(props));
    }

    @Override
    public byte[] toBytes(Object object) {
        return serializeImpl(getSubjectName(this.topic, true), object);
    }
}