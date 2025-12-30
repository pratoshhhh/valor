-- Aggregate soldier exposure data (daily window)
CREATE TABLE soldier_exposure_summary AS
SELECT
    soldier_id,
    COUNT(*) AS total_events,
    COUNT_DISTINCT(CASE WHEN severity = 'CRITICAL' THEN event_id END) AS critical_events,
    COUNT_DISTINCT(CASE WHEN severity = 'HIGH' THEN event_id END) AS high_events,
    COUNT_DISTINCT(CASE WHEN event_type = 'IED_EXPLOSION' THEN event_id END) AS ied_exposures,
    COUNT_DISTINCT(CASE WHEN event_type = 'BURN_PIT_EXPOSURE' THEN event_id END) AS burnpit_exposures,
    COUNT_DISTINCT(CASE WHEN event_type = 'GUNFIRE' THEN event_id END) AS gunfire_exposures,
    AVG(CASE WHEN noise_level_db IS NOT NULL THEN noise_level_db END) AS avg_noise_exposure,
    MAX(CASE WHEN noise_level_db IS NOT NULL THEN noise_level_db END) AS max_noise_exposure,
    MAX(CASE WHEN air_quality_index IS NOT NULL THEN air_quality_index END) AS max_aqi_exposure
FROM battlefield_events_stream
WINDOW TUMBLING (SIZE 1 DAY)
GROUP BY soldier_id
EMIT CHANGES;

-- Count events by device type
CREATE TABLE device_event_counts AS
SELECT
    device_type,
    COUNT(*) AS event_count,
    COUNT_DISTINCT(soldier_id) AS unique_soldiers
FROM battlefield_events_stream
WINDOW TUMBLING (SIZE 1 HOUR)
GROUP BY device_type
EMIT CHANGES;
