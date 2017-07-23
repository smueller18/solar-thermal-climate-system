/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import java.util.HashMap;

public class KeyValuePair {

    public static boolean printValues = true;

    private HashMap<String, Object> keys;
    private HashMap<String, Object> values;

    public KeyValuePair(HashMap<String, Object> keys, HashMap<String, Object> values) {
        this.keys = keys;
        this.values = values;
    }

    public HashMap<String, Object> getKeys() {
        return keys;
    }

    public HashMap<String, Object> getValues() {
        return values;
    }

    public Object getKey(String id) {
        return keys.get(id);
    }

    public Object getValue(String id) {
        return values.get(id);
    }

    @Override
    public String toString() {

        StringBuilder sb = new StringBuilder();

        sb.append("Keys: { ");
        for (String key : this.keys.keySet()) {
            sb.append(String.format("%s: '%s', ", key, this.keys.get(key).toString()));
        }
        sb.append(" }");

        if (printValues) {
            sb.append(", Values: { ");
            for (String key : this.values.keySet()) {
                sb.append(String.format("%s: '%s', ", key, this.values.get(key).toString()));
            }
            sb.append(" }");
        }

        return sb.toString();
    }

}