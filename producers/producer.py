from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.config import KAFKA_CONFIG, SCHEMA_REGISTRY_CONFIG
import uuid
import time
import random
from datetime import datetime

class BattlefieldEventProducer:
    def __init__(self):
        # Schema Registry setup
        self.schema_registry_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONFIG)
        
        # Load schema from file
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'battlefield_event.avsc')
        with open(schema_path, 'r') as f:
            self.schema_str = f.read()
        
        # Avro serializer
        self.avro_serializer = AvroSerializer(
            self.schema_registry_client,
            self.schema_str
        )
        
        # Kafka producer
        self.producer = Producer(KAFKA_CONFIG)
        
        # Base coordinates (Baghdad area)
        self.base_lat = 33.3152
        self.base_lon = 44.3661
    
    def delivery_report(self, err, msg):
        """Callback for delivery reports"""
        if err is not None:
            print(f'❌ Message delivery failed: {err}')
        else:
            print(f'✅ Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}')
    
    def generate_event(self, soldier_id, deployment_day):
        """Generate a realistic battlefield event"""
        
        # Random walk from base coordinates
        lat = self.base_lat + random.uniform(-0.02, 0.02)
        lon = self.base_lon + random.uniform(-0.02, 0.02)
        
        # Event type probabilities (weighted)
        event_weights = {
            'ROUTINE_PATROL': 0.50,
            'TRAINING_EXERCISE': 0.20,
            'BURN_PIT_EXPOSURE': 0.10,
            'GUNFIRE': 0.08,
            'IED_EXPLOSION': 0.05,
            'TOXIC_SMOKE': 0.04,
            'BLAST_INJURY': 0.02,
            'VEHICLE_ACCIDENT': 0.01
        }
        
        event_type = random.choices(
            list(event_weights.keys()),
            weights=list(event_weights.values())
        )[0]
        
        # Severity based on event type
        severity_map = {
            'ROUTINE_PATROL': 'LOW',
            'TRAINING_EXERCISE': 'LOW',
            'BURN_PIT_EXPOSURE': random.choice(['MEDIUM', 'HIGH']),
            'GUNFIRE': random.choice(['MEDIUM', 'HIGH']),
            'IED_EXPLOSION': random.choice(['HIGH', 'CRITICAL']),
            'TOXIC_SMOKE': random.choice(['MEDIUM', 'HIGH']),
            'BLAST_INJURY': 'CRITICAL',
            'VEHICLE_ACCIDENT': random.choice(['MEDIUM', 'HIGH', 'CRITICAL'])
        }
        
        severity = severity_map[event_type]
        
        # Environmental data based on event type
        noise_level = None
        air_quality = None
        
        if event_type in ['IED_EXPLOSION', 'BLAST_INJURY']:
            noise_level = random.uniform(130, 180)
        elif event_type == 'GUNFIRE':
            noise_level = random.uniform(140, 175)
        elif event_type == 'BURN_PIT_EXPOSURE':
            air_quality = random.randint(200, 400)
        elif event_type == 'TOXIC_SMOKE':
            air_quality = random.randint(150, 350)
        
        return {
            'event_id': str(uuid.uuid4()),
            'soldier_id': soldier_id,
            'timestamp': int(time.time() * 1000),
            'latitude': lat,
            'longitude': lon,
            'event_type': event_type,
            'severity': severity,
            'noise_level_db': noise_level,
            'air_quality_index': air_quality,
            'device_id': None,
            'device_type': None,
            'device_manufacturer': None,
            'device_battery_percent': None,
            'signal_strength_dbm': None
        }
    
    def send_event(self, event):
        """Send event to Kafka"""
        try:
            self.producer.produce(
                topic='battlefield-events-raw',
                key=event['soldier_id'],
                value=self.avro_serializer(
                    event,
                    SerializationContext('battlefield-events-raw', MessageField.VALUE)
                ),
                on_delivery=self.delivery_report
            )
            self.producer.poll(0)
        except Exception as e:
            print(f"Error producing message: {e}")
    
    def simulate_deployment(self, soldier_id, duration_hours=8, events_per_hour=3):
        """Simulate a full deployment day"""
        print(f"\n🎖️  Starting deployment simulation for {soldier_id}")
        print(f"Duration: {duration_hours} hours | Events per hour: {events_per_hour}")
        print("-" * 60)
        
        total_events = duration_hours * events_per_hour
        
        for i in range(total_events):
            event = self.generate_event(soldier_id, deployment_day=1)
            self.send_event(event)
            
            if event['severity'] in ['HIGH', 'CRITICAL']:
                print(f"⚠️  {event['event_type']} - Severity: {event['severity']}")
            
            time.sleep(0.5)
        
        self.producer.flush()
        print(f"\n✅ Deployment simulation complete: {total_events} events sent")

if __name__ == "__main__":
    producer = BattlefieldEventProducer()
    
    soldiers = ["SGT_JOHNSON_001", "CPL_MARTINEZ_002", "PFC_WILLIAMS_003"]
    
    for soldier in soldiers:
        producer.simulate_deployment(soldier, duration_hours=2, events_per_hour=4)
        print("\n" + "="*60 + "\n")

