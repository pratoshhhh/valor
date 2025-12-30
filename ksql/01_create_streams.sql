-- Create main event stream from Kafka topic
CREATE STREAM battlefield_events_stream (
    event_id VARCHAR,
    soldier_id VARCHAR,
    timestamp BIGINT,
    latitude DOUBLE,
    longitude DOUBLE,
    event_type VARCHAR,
    severity VARCHAR,
    noise_level_db DOUBLE,
    air_quality_index INT,
    device_id VARCHAR,
    device_type VARCHAR,
    device_manufacturer VARCHAR,
    device_battery_percent INT,
    signal_strength_dbm INT
) WITH (
    KAFKA_TOPIC='battlefield-events-raw',
    VALUE_FORMAT='AVRO',
    TIMESTAMP='timestamp'
);

-- Create stream for high-risk events only
CREATE STREAM high_risk_events AS
SELECT 
    event_id,
    soldier_id,
    timestamp,
    latitude,
    longitude,
    event_type,
    severity,
    noise_level_db,
    air_quality_index,
    device_id
FROM battlefield_events_stream
WHERE severity IN ('HIGH', 'CRITICAL')
EMIT CHANGES;

-- Create stream for burn pit exposures
CREATE STREAM burnpit_exposures AS
SELECT 
    event_id,
    soldier_id,
    timestamp,
    latitude,
    longitude,
    air_quality_index,
    device_id
FROM battlefield_events_stream
WHERE event_type = 'BURN_PIT_EXPOSURE'
EMIT CHANGES;
