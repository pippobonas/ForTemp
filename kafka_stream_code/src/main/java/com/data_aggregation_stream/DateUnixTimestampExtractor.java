package com.data_aggregation_stream;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.streams.processor.TimestampExtractor;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * DateUnixTimestampExtractor is a custom implementation of the TimestampExtractor interface
 * used to extract timestamps from Kafka records. This extractor attempts to parse the 
 * record value as JSON and extract the "date_unix" field, which is assumed to be in 
 * milliseconds. If the "date_unix" field is not present or an error occurs during parsing, 
 * it falls back to using the Kafka record's timestamp.
 */
public class DateUnixTimestampExtractor implements TimestampExtractor {
    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public long extract(ConsumerRecord<Object, Object> record, long previousTimestamp) {
        try {
            // Convert the record value to JSON format
            JsonNode jsonNode = objectMapper.readTree(record.value().toString());
            
            // Extract the "date_unix" value (assuming it is in milliseconds)
            if (jsonNode.has("date_unix")) {
                return jsonNode.get("date_unix").asLong() * 1000;
            } else {
                // If the field is not present, use the Kafka record's timestamp
                System.err.println("[WARN] Missing 'date_unix' field in record: " + record.value());
                return record.timestamp();
            }
        } catch (Exception e) {
            // In case of an error, use the Kafka record's timestamp
            System.err.println("[ERROR] Error parsing record: " + record.value());
            return record.timestamp();
        }
    }
}
