-- Query 1: View live event stream
SELECT * FROM battlefield_events_stream EMIT CHANGES LIMIT 10;

-- Query 2: View soldier summaries
SELECT * FROM soldier_exposure_summary;

-- Query 3: View high-risk events
SELECT * FROM high_risk_events EMIT CHANGES;

-- Query 4: Count events by severity (real-time)
SELECT 
    severity,
    COUNT(*) AS event_count
FROM battlefield_events_stream
WINDOW TUMBLING (SIZE 5 MINUTES)
GROUP BY severity
EMIT CHANGES;

-- Query 5: Find soldiers with multiple IED exposures
SELECT 
    soldier_id,
    COUNT(*) AS ied_count
FROM battlefield_events_stream
WHERE event_type = 'IED_EXPLOSION'
WINDOW TUMBLING (SIZE 1 DAY)
GROUP BY soldier_id
HAVING COUNT(*) > 1
EMIT CHANGES;
