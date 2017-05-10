/**
 * Copyright 2017 Stephan Müller
 * License: MIT
 */

package de.stephanmueller.hska.stcs;

import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.math3.stat.descriptive.moment.Kurtosis;
import org.apache.commons.math3.stat.descriptive.moment.Mean;
import org.apache.commons.math3.stat.descriptive.moment.Skewness;
import org.apache.commons.math3.stat.descriptive.moment.StandardDeviation;
import org.apache.commons.math3.stat.descriptive.rank.Max;
import org.apache.commons.math3.stat.descriptive.rank.Min;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSink;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.PrintSinkFunction;
import org.apache.flink.streaming.api.functions.windowing.AllWindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer010;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer010;
import org.apache.flink.types.NullFieldException;
import org.apache.flink.util.Collector;

import java.security.Key;
import java.util.*;
import java.util.logging.Logger;

public class FeatureExtraction {

    private static final Logger log = Logger.getLogger(FeatureExtraction.class.getName());
    private static List<String> sensorIds = Arrays.asList(
            // prod.stcs.chillii
            "PSOP", "PSOS", "TSOC_1", "TSOC_2", "TSOPO", "TSOPI", "TSOS", "TSH0", "TSH1", "TSH2", "TSH3", "TOU",
            // prod.stcs.roof.solar_radiation
            "total_radiation", "diffuse_radiation",
            // prod.stcs.cellar.flows
            "TVFS_SOP", "FVFS_SOP", "TVFS_C_1", "FVFS_C_1", "TVFS_SOS", "FVFS_SOS"
    );
    private static String schemaRegistryUrl = "http://schema-registry:8082";
    private static String bootstrapServers = "kafka:9092";
    private static String groupId = "machine_learning.aggregations";

    private static String keySchemaRessource = "/key.avsc";
    private static String valueSchemaRessource = "/value.avsc";

    private static String chilliiTopic = "prod.stcs.chillii";
    private static String solarRadiationTopic = "prod.stcs.roof.solar_radiation";
    private static String flowsTopic = "prod.stcs.cellar.flows";

    private static String producerTopicOneMin = "dev.machine_learning.aggregations.1min";
    private static String producerTopicFiveMin = "dev.machine_learning.aggregations.5min";

    public static void main(String[] args) throws Exception {

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        Properties kafkaProps = new Properties();
        kafkaProps.setProperty("bootstrap.servers", bootstrapServers);
        kafkaProps.setProperty("group.id", groupId);

        ConfluentKeyedDeserializationSchema deserializationSchema = new ConfluentKeyedDeserializationSchema(
                schemaRegistryUrl
        );

        ConfluentKeyedSerializationSchema serializationSchemaOneMin = new ConfluentKeyedSerializationSchema(
                schemaRegistryUrl,
                keySchemaRessource,
                valueSchemaRessource,
                producerTopicOneMin
        );

        ConfluentKeyedSerializationSchema serializationSchemaFiveMin = new ConfluentKeyedSerializationSchema(
                schemaRegistryUrl,
                keySchemaRessource,
                valueSchemaRessource,
                producerTopicFiveMin
        );

        DataStream<GenericKeyValueRecord> chilliiStream =
                env.addSource(new FlinkKafkaConsumer010<>(chilliiTopic, deserializationSchema, kafkaProps), chilliiTopic);

        DataStream<GenericKeyValueRecord> solarRadiationStream =
                env.addSource(new FlinkKafkaConsumer010<>(solarRadiationTopic, deserializationSchema, kafkaProps), solarRadiationTopic);

        DataStream<GenericKeyValueRecord> flowsStream =
                env.addSource(new FlinkKafkaConsumer010<>(flowsTopic, deserializationSchema, kafkaProps), flowsTopic);

        DataStream<KeyValuePair> unionStream = chilliiStream.union(solarRadiationStream, flowsStream).flatMap(new Splitter());

        DataStream<KeyValuePair> streamOneMin = unionStream
                .timeWindowAll(Time.minutes(1), Time.seconds(30))
                .apply(new CalcAggregations());

        DataStream<KeyValuePair> streamFiveMin = unionStream
                .timeWindowAll(Time.minutes(5), Time.seconds(150))
                .apply(new CalcAggregations());

        streamOneMin.addSink(new FlinkKafkaProducer010<>(
                producerTopicOneMin,
                serializationSchemaOneMin,
                kafkaProps
        )).name(producerTopicOneMin);

        streamFiveMin.addSink(new FlinkKafkaProducer010<>(
                producerTopicFiveMin,
                serializationSchemaFiveMin,
                kafkaProps
        )).name(producerTopicFiveMin);

        env.execute("Extract features for machine state prediction");
    }

    private static class Splitter implements FlatMapFunction<GenericKeyValueRecord, KeyValuePair> {
        @Override
        public void flatMap(GenericKeyValueRecord genericKeyValueRecord, Collector<KeyValuePair> collector)
                throws Exception {
            try {
                HashMap<String, Object> keys = new HashMap<>();
                HashMap<String, Object> values = new HashMap<>();

                keys.put("timestamp", genericKeyValueRecord.getKey("timestamp"));

                for (String key : FeatureExtraction.sensorIds) {
                    try {
                        values.put(key, genericKeyValueRecord.getValue(key));
                    } catch (NullFieldException e) {
                        continue;
                    }
                }

                collector.collect(new KeyValuePair(keys, values));

            } catch (RuntimeException e) {
                log.warning(e.getMessage());
            }
        }
    }

    private static class CalcAggregations implements AllWindowFunction<KeyValuePair, KeyValuePair, TimeWindow> {

        @Override
        public void apply(TimeWindow window, Iterable<KeyValuePair> keyValuePairs, Collector<KeyValuePair> out)
                throws Exception {

            HashMap<String, ArrayList<Double>> rawValues = new HashMap<>();
            HashMap<String, Object> aggregatedValues = new HashMap<>();
            long timestamp_begin = Long.MAX_VALUE;
            long timestamp_end = Long.MIN_VALUE;

            for (String key : FeatureExtraction.sensorIds) {
                rawValues.put(key, new ArrayList<>());
            }

            for (KeyValuePair kvp : keyValuePairs) {

                timestamp_begin = Math.min((long) kvp.getKey("timestamp"), timestamp_begin);
                timestamp_end = Math.max((long) kvp.getKey("timestamp"), timestamp_end);

                for (String key : FeatureExtraction.sensorIds) {

                    Double value;
                    try {
                        value = (Double) kvp.getValue(key);

                    } catch (ClassCastException e) {
                        value = Double.parseDouble(kvp.getValue(key).toString());
                    }

                    if(value != null)
                        rawValues.get(key).add(value);

                }
            }

            for (String key : rawValues.keySet()) {

                aggregatedValues.put("min_" + key, (float) new Min().evaluate(
                        ArrayUtils.toPrimitive(rawValues.get(key).toArray(new Double[rawValues.get(key).size()]))
                ));

                aggregatedValues.put("max_" + key, (float) new Max().evaluate(
                        ArrayUtils.toPrimitive(rawValues.get(key).toArray(new Double[rawValues.get(key).size()]))
                ));

                aggregatedValues.put("kurtosis_" + key, (float) new Kurtosis().evaluate(
                        ArrayUtils.toPrimitive(rawValues.get(key).toArray(new Double[rawValues.get(key).size()]))
                ));

                aggregatedValues.put("stddev_" + key, (float) new StandardDeviation().evaluate(
                        ArrayUtils.toPrimitive(rawValues.get(key).toArray(new Double[rawValues.get(key).size()]))
                ));

                aggregatedValues.put("mean_" + key, (float) new Mean().evaluate(
                        ArrayUtils.toPrimitive(rawValues.get(key).toArray(new Double[rawValues.get(key).size()]))
                ));

                aggregatedValues.put("skewness_" + key, (float) new Skewness().evaluate(
                        ArrayUtils.toPrimitive(rawValues.get(key).toArray(new Double[rawValues.get(key).size()]))
                ));

            }

            HashMap<String, Object> keys = new HashMap<>();
            keys.put("timestamp_begin", timestamp_begin);
            keys.put("timestamp_end", timestamp_end);

            out.collect(new KeyValuePair(keys, aggregatedValues));
        }
    }
}