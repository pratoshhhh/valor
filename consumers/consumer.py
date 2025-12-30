from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
from google.cloud import firestore
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import KAFKA_CONFIG, SCHEMA_REGISTRY_CONFIG, GCP_PROJECT_ID

class BattlefieldEventConsumer:
    def __init__(self):
        # Schema Registry
        self.schema_registry_client = SchemaRegistryClient(SCHEMA_REGISTRY_CONFIG)
        
        # Avro deserializer
        self.avro_deserializer = AvroDeserializer(
            self.schema_registry_client,
            schema_str=None  # Auto-fetch from registry
        )
        
        # Kafka Consumer Config
        consumer_config = {
            **KAFKA_CONFIG,
            'group.id': 'valorstream-gcp-connector',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        }
        
        self.consumer = Consumer(consumer_config)
        
        # Firestore client
        self.db = firestore.Client(project=GCP_PROJECT_ID)
    
    def process_event(self, event_data):
        """Process event and store in Firestore"""
        try:
            soldier_id = event_data['soldier_id']
            event_id = event_data['event_id']
            
            # Store in Firestore
            doc_ref = self.db.collection('soldiers').document(soldier_id)\
                             .collection('service_record').document(event_id)
            
            doc_ref.set({
                'event_id': event_id,
                'timestamp': event_data['timestamp'],
                'location': {
                    'latitude': event_data['latitude'],
                    'longitude': event_data['longitude']
                },
                'event_type': event_data['event_type'],
                'severity': event_data['severity'],
                'noise_level_db': event_data.get('noise_level_db'),
                'air_quality_index': event_data.get('air_quality_index'),
                'device_id': event_data.get('device_id'),
                'device_type': event_data.get('device_type'),
                'processed_at': firestore.SERVER_TIMESTAMP
            })
            
            print(f"✅ Stored event {event_id} for {soldier_id}")
            
            # If high severity, log alert
            if event_data['severity'] in ['HIGH', 'CRITICAL']:
                print(f"⚠️  HIGH RISK: {event_data['event_type']} - {soldier_id}")
                self.create_alert(soldier_id, event_data)
            
        except Exception as e:
            print(f"❌ Error processing event: {e}")
    
    def create_alert(self, soldier_id, event_data):
        """Create alert in Firestore"""
        alert_ref = self.db.collection('health_alerts').document()
        alert_ref.set({
            'soldier_id': soldier_id,
            'event_id': event_data['event_id'],
            'alert_type': 'IMMEDIATE_MEDICAL_EVALUATION',
            'severity': event_data['severity'],
            'message': f"Soldier exposed to {event_data['event_type']}",
            'created_at': firestore.SERVER_TIMESTAMP,
            'resolved': False
        })
    
    def start_consuming(self, topics=['battlefield-events-raw']):
        """Start consuming from Kafka topics"""
        self.consumer.subscribe(topics)
        
        print(f"🎧 Consumer started. Listening to: {', '.join(topics)}")
        print("-" * 60)
        
        message_count = 0
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    print(".", end="", flush=True)  # Show it's polling
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        print(f"\n📍 Reached end of partition")
                        continue
                    else:
                        print(f"\n❌ Consumer error: {msg.error()}")
                    continue
                
                # If we get here, we have a message!
                print(f"\n📨 Received message from partition {msg.partition()}, offset {msg.offset()}")
                
                # Deserialize
                try:
                    event_data = self.avro_deserializer(
                        msg.value(),
                        SerializationContext(msg.topic(), MessageField.VALUE)
                    )
                    
                    if event_data:
                        print(f"📦 Deserialized event: {event_data.get('event_id')}")
                        self.process_event(event_data)
                        message_count += 1
                        print(f"✅ Total messages processed: {message_count}")
                    
                except Exception as e:
                    print(f"❌ Error deserializing: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Commit offset
                self.consumer.commit(asynchronous=False)
                
        except KeyboardInterrupt:
            print("\n🛑 Consumer stopped by user")
        finally:
            self.consumer.close()
            print(f"Consumer closed. Total messages processed: {message_count}")
            
if __name__ == "__main__":
    consumer = BattlefieldEventConsumer()
    consumer.start_consuming()

