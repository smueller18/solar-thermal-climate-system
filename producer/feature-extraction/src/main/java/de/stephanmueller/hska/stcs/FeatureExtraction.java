/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import com.github.smueller18.avro.builder.AvroBuilder;
import com.github.smueller18.flink.serialization.AvroBuilderKeyedSerializationSchema;
import com.github.smueller18.flink.serialization.GenericKeyValueRecord;
import com.github.smueller18.flink.serialization.SchemaRegistryKeyedDeserializationSchema;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.timestamps.AscendingTimestampExtractor;
import org.apache.flink.streaming.api.functions.windowing.AllWindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer010;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer010;
import org.apache.flink.util.Collector;

import java.util.*;
import java.util.logging.Logger;

public class FeatureExtraction {

    private static final Logger log = Logger.getLogger(FeatureExtraction.class.getName());
    private static List<String> sensorIds = Arrays.asList(
            // prod.stcs.chillii
            "PSOP", "PSOS", "TSOS", "TSH0", "TSH1", "TSH2", "TSH3", "TOU",
            // prod.stcs.roof.solar_radiation
            "total_radiation",
            // prod.stcs.cellar.flows
            "FVFS_SOP", "FVFS_SOS"
    );
    private static String schemaRegistryUrl = "http://schema-registry:8082";
    private static String bootstrapServers = "kafka:9092";
    private static String groupId = "machine_learning.aggregations";

    private static String chilliiTopic = "prod.stcs.chillii";
    private static String solarRadiationTopic = "prod.stcs.roof.solar_radiation";
    private static String flowsTopic = "prod.stcs.cellar.flows";


    public static void main(String[] args) throws Exception {

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);

        Properties kafkaProps = new Properties();
        kafkaProps.setProperty("bootstrap.servers", bootstrapServers);
        kafkaProps.setProperty("group.id", groupId);

        Properties schemaRegistryProps = new Properties();
        schemaRegistryProps.setProperty("schema.registry.url", schemaRegistryUrl);

        SchemaRegistryKeyedDeserializationSchema deserializationSchema = new SchemaRegistryKeyedDeserializationSchema(
                schemaRegistryProps
        );

        DataStream<GenericKeyValueRecord> chilliiStream =
                env.addSource(new FlinkKafkaConsumer010<>(chilliiTopic, deserializationSchema, kafkaProps), chilliiTopic);

        DataStream<GenericKeyValueRecord> solarRadiationStream =
                env.addSource(new FlinkKafkaConsumer010<>(solarRadiationTopic, deserializationSchema, kafkaProps), solarRadiationTopic);

        DataStream<GenericKeyValueRecord> flowsStream =
                env.addSource(new FlinkKafkaConsumer010<>(flowsTopic, deserializationSchema, kafkaProps), flowsTopic);

        DataStream<GenericKeyValueRecord> unionStream = chilliiStream
                .union(solarRadiationStream, flowsStream)
                .assignTimestampsAndWatermarks(new TimeStampExtractor());

        DataStream<Aggregations> streamFiveMin = unionStream
                .timeWindowAll(Time.minutes(10), Time.seconds(10))
                .apply(new PackValues());

        streamFiveMin.addSink(new FlinkKafkaProducer010<>(
                AvroBuilder.getTopicName(Aggregations.class),
                new AvroBuilderKeyedSerializationSchema<>(schemaRegistryProps),
                kafkaProps
        )).name(AvroBuilder.getTopicName(Aggregations.class));

        // streamFiveMin.print();

        env.execute("Extract features for machine state prediction");
    }

    private static class TimeStampExtractor extends AscendingTimestampExtractor<GenericKeyValueRecord> {
        @Override
        public long extractAscendingTimestamp(GenericKeyValueRecord genericKeyValueRecord) {
            return (Long) genericKeyValueRecord.getKey("timestamp");
        }
    }

    //private static class PairValues

   private static class PackValues implements AllWindowFunction<GenericKeyValueRecord, Aggregations, TimeWindow> {

        @Override
        public void apply(TimeWindow window, Iterable<GenericKeyValueRecord> genericKeyValueRecords, Collector<Aggregations> out)
                throws Exception {

            HashMap<String, ArrayList<Double>> rawValues = new HashMap<>();
            long timestampBegin = Long.MAX_VALUE;
            long timestampEnd = Long.MIN_VALUE;

            for (String key : FeatureExtraction.sensorIds) {
                rawValues.put(key + "_t1", new ArrayList<>());
                rawValues.put(key + "_t2", new ArrayList<>());
            }

            for (GenericKeyValueRecord genericKeyValueRecord : genericKeyValueRecords) {
                timestampBegin = Math.min((long) genericKeyValueRecord.getKey("timestamp"), timestampBegin);
                timestampEnd = Math.max((long) genericKeyValueRecord.getKey("timestamp"), timestampEnd);
            }

            long timestampSplit = timestampBegin + (timestampEnd - timestampBegin) / 2;

            for (GenericKeyValueRecord genericKeyValueRecord : genericKeyValueRecords) {

                for (String key : FeatureExtraction.sensorIds) {

                    Double value;
                    try {
                        try {
                            value = (Double) genericKeyValueRecord.getValue(key);
                        }
                        catch (NullPointerException e) {
                            value = null;
                        }

                    } catch (ClassCastException e) {
                        try {
                            value = Double.parseDouble(genericKeyValueRecord.getValue(key).toString());
                        }
                        catch (NullPointerException e2) {
                            value = null;
                        }
                    }

                    if (value != null) {
                        if ((long) genericKeyValueRecord.getKey("timestamp") < timestampSplit)
                            rawValues.get(key + "_t1").add(value);
                        else
                            rawValues.get(key + "_t2").add(value);
                    }

                }
            }

            try {
                out.collect(new Aggregations(
                        timestampBegin,
                        timestampEnd,
                        rawValues
                ));
            }
            catch(Exception e) {
                log.warning("Set of values could not be determined");
            }

        }
    }
}
