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

# Add after imports, before the class
print("=" * 60)
print("DEBUG: Configuration Check")
print("=" * 60)
print(f"Bootstrap Server: {KAFKA_CONFIG.get('bootstrap.servers')}")
print(f"API Key: {KAFKA_CONFIG.get('sasl.username')[:10]}..." if KAFKA_CONFIG.get('sasl.username') else "None")
print(f"Schema Registry URL: {SCHEMA_REGISTRY_CONFIG.get('url')}")
print("=" * 60)

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
        """
        Generate a realistic battlefield event
        UNCHANGED - keeps your original event generation logic
        """
        
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
        """Send event to Kafka - UNCHANGED"""
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
            print(f"❌ Error producing message: {e}")
            import traceback
            traceback.print_exc()

    def simulate_deployment(self, soldier_id, duration_hours=8, events_per_hour=3):
        """
        Simulate a full deployment day
        ENHANCED: Added better logging and summary stats
        """
        print(f"\n🎖️  Starting deployment simulation for {soldier_id}")
        print(f"Duration: {duration_hours} hours | Events per hour: {events_per_hour}")
        print("-" * 60)
        
        total_events = duration_hours * events_per_hour
        
        # Track event statistics
        severity_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        event_type_counts = {}
        
        for i in range(total_events):
            event = self.generate_event(soldier_id, deployment_day=1)
            self.send_event(event)
            
            # Track statistics
            severity_counts[event['severity']] += 1
            event_type_counts[event['event_type']] = event_type_counts.get(event['event_type'], 0) + 1
            
            # Enhanced logging for important events
            if event['severity'] in ['HIGH', 'CRITICAL']:
                print(f"⚠️  {event['event_type']} - Severity: {event['severity']}")
                if event.get('noise_level_db'):
                    print(f"   📊 Noise: {event['noise_level_db']:.1f} dB")
                if event.get('air_quality_index'):
                    print(f"   📊 AQI: {event['air_quality_index']}")
            
            # Shorter delay for more realistic real-time simulation
            time.sleep(0.5)
        
        self.producer.flush()
        
        # Print summary
        print(f"\n✅ Deployment simulation complete: {total_events} events sent")
        print(f"\n📊 Severity Summary:")
        for severity, count in severity_counts.items():
            if count > 0:
                percentage = (count / total_events) * 100
                print(f"   {severity}: {count} ({percentage:.1f}%)")
        
        print(f"\n📋 Top Event Types:")
        sorted_events = sorted(event_type_counts.items(), key=lambda x: x[1], reverse=True)
        for event_type, count in sorted_events[:5]:
            print(f"   {event_type}: {count}")

    def simulate_continuous(self, soldiers, interval_seconds=30):
        """
        ENHANCEMENT: New method for continuous event generation
        Simulates ongoing operations with events every interval_seconds
        Perfect for dashboard real-time testing
        """
        print(f"\n🔄 Starting continuous simulation")
        print(f"Soldiers: {', '.join(soldiers)}")
        print(f"Event interval: {interval_seconds} seconds")
        print(f"Press Ctrl+C to stop")
        print("-" * 60)
        
        event_count = 0
        
        try:
            while True:
                # Random soldier
                soldier_id = random.choice(soldiers)
                
                # Generate and send event
                event = self.generate_event(soldier_id, deployment_day=1)
                self.send_event(event)
                event_count += 1
                
                # Log
                severity_icon = '🔴' if event['severity'] == 'CRITICAL' else '🟠' if event['severity'] == 'HIGH' else '🟡' if event['severity'] == 'MEDIUM' else '🟢'
                print(f"{severity_icon} Event #{event_count}: {event['event_type']} - {soldier_id} ({event['severity']})")
                
                # Wait
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Continuous simulation stopped")
            print(f"Total events generated: {event_count}")
            self.producer.flush()

if __name__ == "__main__":
    producer = BattlefieldEventProducer()
    
    # Your original soldiers
    soldiers = ["SGT_JOHNSON_001", "CPL_MARTINEZ_002", "PFC_WILLIAMS_003"]
    
    # OPTION 1: Original batch simulation (YOUR ORIGINAL CODE)
    # Uncomment to use:
    # for soldier in soldiers:
    #     producer.simulate_deployment(soldier, duration_hours=2, events_per_hour=4)
    #     print("\n" + "="*60 + "\n")
    
    # OPTION 2: Continuous simulation (NEW - great for dashboard testing)
    # Events every 30 seconds for real-time dashboard updates
    producer.simulate_continuous(soldiers, interval_seconds=30)