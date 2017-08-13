
package de.stephanmueller.hska.stcs;

import com.github.smueller18.avro.builder.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

@KafkaTopic(namespace = "prod.machine_learning", name = "aggregations_10minutes")
class Aggregations extends AvroBuilder {
    @Key
    @TimestampMillisType
    public long timestamp_begin;

    @Key
    @TimestampMillisType
    public long timestamp_end;

    @Value
    public ArrayList<Double> psop_t1;
    @Value
    public ArrayList<Double> psos_t1;
    @Value
    public ArrayList<Double> tsos_t1;
    @Value
    public ArrayList<Double> tsh0_t1;
    @Value
    public ArrayList<Double> tsh1_t1;
    @Value
    public ArrayList<Double> tsh2_t1;
    @Value
    public ArrayList<Double> tsh3_t1;
    @Value
    public ArrayList<Double> tou_t1;
    @Value
    public ArrayList<Double> glob_t1;
    @Value
    public ArrayList<Double> fvfs_sop_t1;
    @Value
    public ArrayList<Double> fvfs_sos_t1;

    @Value
    public ArrayList<Double> psop_t2;
    @Value
    public ArrayList<Double> psos_t2;
    @Value
    public ArrayList<Double> tsos_t2;
    @Value
    public ArrayList<Double> tsh0_t2;
    @Value
    public ArrayList<Double> tsh1_t2;
    @Value
    public ArrayList<Double> tsh2_t2;
    @Value
    public ArrayList<Double> tsh3_t2;
    @Value
    public ArrayList<Double> tou_t2;
    @Value
    public ArrayList<Double> glob_t2;
    @Value
    public ArrayList<Double> fvfs_sop_t2;
    @Value
    public ArrayList<Double> fvfs_sos_t2;


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
            if (!(rawValues.containsKey(id + "_t1") && rawValues.containsKey(id + "_t2")))
                throw new RuntimeException("aggregations does not contain all sensor ids");

            else if (rawValues.get(id + "_t1").isEmpty() || rawValues.get(id + "_t2").isEmpty())
                throw new RuntimeException("at least one of the aggregations is empty");
        }

        this.timestamp_begin = timestamp_begin;
        this.timestamp_end = timestamp_end;
        this.psop_t1 = rawValues.get("PSOP_t1");
        this.psos_t1 = rawValues.get("PSOS_t1");
        this.tsos_t1 = rawValues.get("TSOS_t1");
        this.tsh0_t1 = rawValues.get("TSH0_t1");
        this.tsh1_t1 = rawValues.get("TSH1_t1");
        this.tsh2_t1 = rawValues.get("TSH2_t1");
        this.tsh3_t1 = rawValues.get("TSH3_t1");
        this.tou_t1 = rawValues.get("TOU_t1");
        this.glob_t1 = rawValues.get("total_radiation_t1");
        this.fvfs_sop_t1 = rawValues.get("FVFS_SOP_t1");
        this.fvfs_sos_t1 = rawValues.get("FVFS_SOS_t1");

        this.psop_t2 = rawValues.get("PSOP_t2");
        this.psos_t2 = rawValues.get("PSOS_t2");
        this.tsos_t2 = rawValues.get("TSOS_t2");
        this.tsh0_t2 = rawValues.get("TSH0_t2");
        this.tsh1_t2 = rawValues.get("TSH1_t2");
        this.tsh2_t2 = rawValues.get("TSH2_t2");
        this.tsh3_t2 = rawValues.get("TSH3_t2");
        this.tou_t2 = rawValues.get("TOU_t2");
        this.glob_t2 = rawValues.get("total_radiation_t2");
        this.fvfs_sop_t2 = rawValues.get("FVFS_SOP_t2");
        this.fvfs_sos_t2 = rawValues.get("FVFS_SOS_t2");
    }

    @Override
    public String toString() {
        return "begin " + this.timestamp_begin + " end " + timestamp_end + "\n"
                + "psop_t1: " + this.psop_t1 + "\n"
                + "psos_t1: " + this.psos_t1 + "\n"
                + "tsos_t1: " + this.tsos_t1 + "\n"
                + "tsh0_t1: " + this.tsh0_t1 + "\n"
                + "tsh1_t1: " + this.tsh1_t1 + "\n"
                + "tsh2_t1: " + this.tsh2_t1 + "\n"
                + "tsh3_t1: " + this.tsh3_t1 + "\n"
                + "tou_t1: " + this.tou_t1 + "\n"
                + "glob_t1: " + this.glob_t1 + "\n"
                + "FVFS_SOP_t1: " + this.fvfs_sop_t1 + "\n"
                + "FVFS_SOS_t1: " + this.fvfs_sos_t1 + "\n"

                + "psop_t2: " + this.psop_t2 + "\n"
                + "psos_t2: " + this.psos_t2 + "\n"
                + "tsos_t2: " + this.tsos_t2 + "\n"
                + "tsh0_t2: " + this.tsh0_t2 + "\n"
                + "tsh1_t2: " + this.tsh1_t2 + "\n"
                + "tsh2_t2: " + this.tsh2_t2 + "\n"
                + "tsh3_t2: " + this.tsh3_t2 + "\n"
                + "tou_t2: " + this.tou_t2 + "\n"
                + "glob_t2: " + this.glob_t2 + "\n"
                + "FVFS_SOP_t2: " + this.fvfs_sop_t2 + "\n"
                + "FVFS_SOS_t2: " + this.fvfs_sos_t2 + "\n";
    }
}
