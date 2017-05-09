/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import org.apache.avro.generic.GenericRecord;
import org.apache.flink.types.NullFieldException;

import java.util.logging.Logger;

public class GenericKeyValueRecord {

    private static final Logger log = Logger.getLogger( GenericKeyValueRecord.class.getName() );

    private GenericRecord key;
    private GenericRecord value;

    public GenericKeyValueRecord(GenericRecord key, GenericRecord value) {
        this.key = key;
        this.value = value;
    }

    public GenericRecord getKey() {
        return key;
    }

    public GenericRecord getValue() {
        return value;
    }

    public Object getKey(String id) throws RuntimeException {
        try {
            return key.get(id);
        }
        catch(RuntimeException e){
            throw new RuntimeException("Error while trying to get element with id " + id + ". ", e);
        }
    }

    public Object getValue(String id) throws RuntimeException {

        if (value.get(id) == null)
            throw new NullFieldException("Element with id '" + id + "' is Null.");
        return value.get(id);
    }
}
