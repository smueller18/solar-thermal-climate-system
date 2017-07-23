
package de.stephanmueller.hska.stcs;

import com.github.smueller18.avro.builder.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

@KafkaTopic(namespace = "dev.machine_learning", name = "aggregations_5min")
class Aggregations extends AvroBuilder {
    @Key
    @TimestampMillisType
    public long timestamp_begin;

    @Key
    @TimestampMillisType
    public long timestamp_end;

    @Value
    public ArrayList<Double> psop;
    @Value
    public ArrayList<Double> psos;
    @Value
    public ArrayList<Double> tsos;
    @Value
    public ArrayList<Double> tsh0;
    @Value
    public ArrayList<Double> tsh1;
    @Value
    public ArrayList<Double> tsh2;
    @Value
    public ArrayList<Double> tsh3;
    @Value
    public ArrayList<Double> tou;
    @Value
    public ArrayList<Double> glob;
    @Value
    public ArrayList<Double> fvfs_sop;
    @Value
    public ArrayList<Double> fvfs_sos;

    public Aggregations() {

    }

    public Aggregations(long timestamp_begin, long timestamp_end, HashMap<String, ArrayList<Double>> rawValues) throws RuntimeException {

        List<String> sensorIds = Arrays.asList(
                // prod.stcs.chillii
                "PSOP", "PSOS", "TSOS", "TSH0", "TSH1", "TSH2", "TSH3", "TOU",
                // prod.stcs.roof.solar_radiation
                "total_radiation",
                // prod.stcs.cellar.flows
                "FVFS_SOP", "FVFS_SOS"
        );

        for (String id : sensorIds) {
            if (!rawValues.containsKey(id))
                throw new RuntimeException("aggregations does not contain all sensor ids");

            else if (rawValues.get(id).isEmpty())
                throw new RuntimeException("at least one of the aggregations is empty");
        }

        this.timestamp_begin = timestamp_begin;
        this.timestamp_end = timestamp_end;
        this.psop = rawValues.get("PSOP");
        this.psos = rawValues.get("PSOS");
        this.tsos = rawValues.get("TSOS");
        this.tsh0 = rawValues.get("TSH0");
        this.tsh1 = rawValues.get("TSH1");
        this.tsh2 = rawValues.get("TSH2");
        this.tsh3 = rawValues.get("TSH3");
        this.tou = rawValues.get("TOU");
        this.glob = rawValues.get("total_radiation");
        this.fvfs_sop = rawValues.get("FVFS_SOP");
        this.fvfs_sos = rawValues.get("FVFS_SOS");
    }

    @Override
    public String toString() {
        return "begin " + this.timestamp_begin + " end " + timestamp_end + "\n"
                + "psop: " + this.psop + "\n"
                + "psos: " + this.psos + "\n"
                + "tsos: " + this.tsos + "\n"
                + "tsh0: " + this.tsh0 + "\n"
                + "tsh1: " + this.tsh1 + "\n"
                + "tsh2: " + this.tsh2 + "\n"
                + "tsh3: " + this.tsh3 + "\n"
                + "tou: " + this.tou + "\n"
                + "glob: " + this.glob + "\n"
                + "FVFS_SOP: " + this.fvfs_sop + "\n"
                + "FVFS_SOS: " + this.fvfs_sos + "\n";
    }
}