from confluent_kafka import Consumer
from config.config import KAFKA_CONFIG

def replay_soldier_events(soldier_id, from_timestamp=None):
    """Replay events for a specific soldier"""
    
    consumer_config = {
        **KAFKA_CONFIG,
        'group.id': f'replay-{soldier_id}',
        'auto.offset.reset': 'earliest'  # Start from beginning
    }
    
    consumer = Consumer(consumer_config)
    consumer.subscribe(['battlefield-events-raw'])
    
    print(f"🔄 Replaying events for {soldier_id}")
    events = []
    
    try:
        while True:
            msg = consumer.poll(timeout=5.0)
            if msg is None:
                break
            
            if msg.error():
                continue
            
            # Check if message is for target soldier
            if msg.key().decode('utf-8') == soldier_id:
                events.append(msg.value())
                print(f"Found event at offset: {msg.offset()}")
    
    finally:
        consumer.close()
    
    print(f"✅ Retrieved {len(events)} events for {soldier_id}")
    return events

if __name__ == "__main__":
    replay_soldier_events("SGT_JOHNSON_001")