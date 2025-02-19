package com.data_aggregation_stream;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;

import org.apache.kafka.connect.json.JsonDeserializer;
import org.apache.kafka.connect.json.JsonSerializer;

import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.common.utils.Bytes;

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.streams.KeyValue;
import org.apache.kafka.streams.kstream.TimeWindows;
import org.apache.kafka.streams.kstream.Windowed;
import org.apache.kafka.streams.state.WindowStore;

import java.time.Duration;
import java.util.Properties;
import java.io.InputStream;

/**
 * The KafkaStreamsWarmUp class sets up and runs a Kafka Streams application that processes weather data.
 * It reads configuration properties from a file and environment variables, sets up the Kafka Streams topology,
 * and starts the stream processing.
 * 
 * The application performs the following steps:
 * 1. Loads properties from the "application.properties" file.
 * 2. Overrides properties with environment variables if available.
 * 3. Configures Kafka Streams properties.
 * 4. Builds a Kafka Streams topology to process weather data.
 * 5. Groups the data by a composite key (latitude_longitude).
 * 6. Configures a hopping window with a 4-hour window size and 1-hour advance.
 * 7. Aggregates the data within the window, keeping track of the latest hour and adding new values to the list.
 * 8. Converts the aggregated KTable to a stream and filters results where the list size is 4.
 * 9. Maps the filtered results to a new JSON message with the latest and lagged values.
 * 10. Sends the results to the output topic.
 * 11. Starts the Kafka Streams application and adds a shutdown hook to close the streams on exit.
 * 
 * Properties:
 * - application.id: The application ID for the Kafka Streams application.
 * - bootstrap.servers: The Kafka bootstrap servers.
 * - default.key.serde: The default key serializer/deserializer class.
 * - default.value.serde: The default value serializer/deserializer class.
 * - input.topic: The input Kafka topic for weather data.
 * - output.topic: The output Kafka topic for aggregated weather data.
 * - window.size.hrs: The size of the hopping window in hours (default: 4).
 * - window.size.plus.min: Additional minutes to add to the window size (default: 10).
 * - window.advance.hrs: The advance interval for the hopping window in hours (default: 1).
 * 
 * Environment Variables:
 * - APPLICATION_ID: Overrides the application ID.
 * - KAFKA_BOOTSTRAP_SERVERS: Overrides the Kafka bootstrap servers.
 * - DEFAULT_KEY_SERDE: Overrides the default key serializer/deserializer class.
 * - DEFAULT_VALUE_SERDE: Overrides the default value serializer/deserializer class.
 * - DEFAULT_TIMESTAMP_EXTRACTOR: Overrides the default timestamp extractor class.
 * - INPUT_TOPIC: Overrides the input Kafka topic.
 * - OUTPUT_TOPIC: Overrides the output Kafka topic.
 */

public class KafkaStreamsWarmUp {
    /**
     * A static instance of ObjectMapper used for JSON serialization and deserialization.
     * ObjectMapper is a class from the Jackson library that provides functionality for 
     * reading and writing JSON, either to and from basic POJOs (Plain Old Java Objects) 
     * or to and from a general-purpose JSON Tree Model (JsonNode), as well as related 
     * functionality for performing conversions.
     */
    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Overrides the specified configuration property with the value of the given environment variable, if it exists.
     *
     * @param props     The Properties object to update.
     * @param configKey The key of the property to override.
     * @param envVar    The name of the environment variable to use for the override.
     */
    private static void overridePropertiesWithEnv(Properties props, String configKey, String envVar) {
        String envValue = System.getenv(envVar);
        if (envValue != null) {
            props.put(configKey, envValue);
        }
    }

    
    /**
     * Retrieves a property value from the provided Properties object, with the option to override it
     * with an environment variable. If neither the property nor the environment variable is set,
     * a default value is returned.
     *
     * @param props         the Properties object containing the property values
     * @param propertyKey   the key of the property to retrieve
     * @param envVar        the name of the environment variable that can override the property value
     * @param defaultValue  the default value to return if the property and environment variable are not set
     * @return              the property value, overridden by the environment variable if it is set, 
     *                      or the default value if neither is set
     */
    private static String getPropertyWithEnvOverride(Properties props, String propertyKey, String envVar, String defaultValue) {
        String propertyValue = props.getProperty(propertyKey, defaultValue);
        String envValue = System.getenv(envVar);
        return (envValue != null) ? envValue : propertyValue;
    }

    /**
     * The main method initializes and starts a Kafka Streams application.
     * It reads configuration properties from an external file and environment variables,
     * sets up the stream processing topology, and starts the Kafka Streams instance.
     *
     * @param args Command line arguments (not used).
     *
     * The method performs the following steps:
     * 1. Loads properties from "application.properties" file.
     * 2. Overrides properties with system environment variables if available.
     * 3. Retrieves window size and advance interval from properties.
     * 4. Sets up a Kafka Streams builder and defines the stream processing topology:
     *    - Reads data from the input topic.
     *    - Groups the data by a composite key (latitude_longitude).
     *    - Configures a hopping window with a specified size and advance interval.
     *    - Aggregates the data within the window.
     *    - Converts the aggregated KTable to a stream and filters results.
     *    - Maps the filtered results to a new format and sends them to the output topic.
     * 5. Starts the Kafka Streams instance and adds a shutdown hook to close it gracefully.
     */
    public static void main(String[] args) {
        Properties props = new Properties();
        try (InputStream input = KafkaStreamsWarmUp.class.getClassLoader().getResourceAsStream("application.properties")) {
            if (input == null) {
                System.out.println("Sorry, unable to find application.properties");
                return;
            }
            props.load(input);
        } catch (Exception ex) {
            ex.printStackTrace();
        }

        props.put(StreamsConfig.APPLICATION_ID_CONFIG, props.getProperty("application.id"));
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, props.getProperty("default.key.serde"));
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, props.getProperty("default.value.serde"));
        props.put(StreamsConfig.DEFAULT_TIMESTAMP_EXTRACTOR_CLASS_CONFIG, DateUnixTimestampExtractor.class);

        // Override properties with system environment variables if available
        overridePropertiesWithEnv(props, StreamsConfig.APPLICATION_ID_CONFIG, "APPLICATION_ID");
        overridePropertiesWithEnv(props, StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "KAFKA_BOOTSTRAP_SERVERS");
        

        final int WINDOW_SIZE_HOURS = Integer.parseInt(getPropertyWithEnvOverride(props, "window.size.hrs", "WINDOW_SIZE_HOURS", "4"));
        final int WINDOW_SIZE_PLUS_MINUTES = Integer.parseInt(getPropertyWithEnvOverride(props, "window.size.plus.min", "WINDOW_SIZE_PLUS_MINUTES", "59"));
        final int WINDOW_ADVANCE_HOURS = Integer.parseInt(getPropertyWithEnvOverride(props, "window.advance.hrs", "WINDOW_ADVANCE_HOURS", "1"));
        final String INPUT_TOPIC = getPropertyWithEnvOverride(props, "input.topic", "INPUT_TOPIC", "current-weather");
        final String OUTPUT_TOPIC = getPropertyWithEnvOverride(props, "output.topic", "OUTPUT_TOPIC", "weather-data-aggregated");

        final int SECOND_IN_HOUR = 3600;
        final int SECOND_IN_DAY = 86400;

        StreamsBuilder builder = new StreamsBuilder();
       
        final Serializer<JsonNode> jsonSerializer = new JsonSerializer();
        final Deserializer<JsonNode> jsonDeserializer = new JsonDeserializer();
        final Serde<JsonNode> jsonSerde = Serdes.serdeFrom(jsonSerializer, jsonDeserializer);

        KStream<String, JsonNode> sourceStream = builder.stream(INPUT_TOPIC, 
            Consumed.with(Serdes.String(), jsonSerde));

        // Group the data by a composite key (latitude_longitude)
        KGroupedStream<String, JsonNode> groupedStream = sourceStream.groupBy(
            (key, value) -> {
                String city = value.has("city") ? value.get("city").asText() : "unknown";
                return city;
            },
            Grouped.with(Serdes.String(), jsonSerde)
        );
        
        // Configure a hopping window with a 4-hour window size and 1-hour advance
        TimeWindowedKStream<String, JsonNode> timeWindowedStream = groupedStream
        .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofHours(WINDOW_SIZE_HOURS).plusMinutes(WINDOW_SIZE_PLUS_MINUTES))
            .advanceBy(Duration.ofHours(WINDOW_ADVANCE_HOURS)));
        

        KTable<Windowed<String>, JsonNode> aggregatedTable = timeWindowedStream.aggregate(
            () -> {
                ObjectNode initialValue = JsonNodeFactory.instance.objectNode();
                initialValue.set("list", JsonNodeFactory.instance.arrayNode());
                initialValue.set("latest_hour", JsonNodeFactory.instance.numberNode(-1));
                return initialValue;
            },
            (key, value, aggregate) -> {
                ObjectNode list = (ObjectNode) aggregate;
                ArrayNode values = (ArrayNode) list.get("list");
                int hour_unix = value.has("date_unix") ? (value.get("date_unix").asInt() % SECOND_IN_DAY)/SECOND_IN_HOUR : -1;
                // Add the new value to the list if the hour is greater than the latest (if at least one hour has passed)
                if (list.get("latest_hour").asInt() < hour_unix) {
                    list.set("latest_hour", JsonNodeFactory.instance.numberNode(hour_unix));
                    values.add(value);
                }
                
                list.set("list", values);
                return list;
            },
                Materialized.<String, JsonNode, WindowStore<Bytes, byte[]>>as("hop-store")
                .withKeySerde(Serdes.String())
                .withValueSerde(jsonSerde)
        );
            
        // Convert the aggregated KTable to a stream and filter results
    
        KStream<String, String> resultStream = aggregatedTable
            .toStream()
            .filter((key, value) -> ((ArrayNode) value.get("list")).size() == 4)
            .map((key, value) -> {
                // Create new message with passed values
                ObjectNode resultJson = objectMapper.createObjectNode();

                int valuesSize = ((ArrayNode) value.get("list")).size();

                ArrayNode values = (ArrayNode) value.get("list");
                JsonNode latestValue = values.get(valuesSize-1);
                JsonNode secondLatestValue = values.get(valuesSize-2);
                JsonNode thirdLatestValue = values.get(valuesSize-3);
                JsonNode fourthLatestValue = values.get(valuesSize-4);

                if (latestValue.has("@timestamp")) resultJson.put("@timestamp", latestValue.get("@timestamp").asText());
                if (latestValue.has("latitude")) resultJson.put("latitude", latestValue.get("latitude").asDouble());
                if (latestValue.has("longitude")) resultJson.put("longitude", latestValue.get("longitude").asDouble());
                if (latestValue.has("date_unix")) resultJson.put("date_unix", latestValue.get("date_unix").asInt()); 
                if (latestValue.has("wind_speed")) resultJson.put("wind_speed", latestValue.get("wind_speed").asDouble());
                if (latestValue.has("msl")) resultJson.put("msl", latestValue.get("msl").asDouble());
                if (latestValue.has("tcc")) resultJson.put("tcc", latestValue.get("tcc").asDouble());
                if (latestValue.has("tp")) resultJson.put("tp", latestValue.get("tp").asDouble());
                if (latestValue.has("sp")) resultJson.put("sp", latestValue.get("sp").asDouble());
                if (latestValue.has("ssrd")) resultJson.put("ssrd", latestValue.get("ssrd").asDouble());
                if (latestValue.has("city")) resultJson.put("city", latestValue.get("city").asText());
                if (latestValue.has("humidity")) resultJson.put("humidity", latestValue.get("humidity").asDouble());
                if (latestValue.has("2t")) resultJson.put("2t", latestValue.get("2t").asDouble());
                if (secondLatestValue.has("2t")) resultJson.put("2t_lag_1h", secondLatestValue.get("2t").asDouble());
                if (thirdLatestValue.has("2t")) resultJson.put("2t_lag_2h", thirdLatestValue.get("2t").asDouble());
                if (fourthLatestValue.has("2t")) resultJson.put("2t_lag_3h", fourthLatestValue.get("2t").asDouble());

                return new KeyValue<>(key.key(), resultJson.toString());
            });
        resultStream.to(OUTPUT_TOPIC, Produced.with(Serdes.String(), Serdes.String()));
        
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
        
    }

}

