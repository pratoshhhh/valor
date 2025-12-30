"""
Process and validate battlefield events
"""

from google.cloud import firestore
from datetime import datetime
import uuid


class EventProcessor:
    def __init__(self, firestore_client):
        self.db = firestore_client
    
    def validate_event(self, event):
        """Validate event has required fields"""
        required_fields = [
            'event_id', 'soldier_id', 'timestamp', 
            'latitude', 'longitude', 'event_type', 'severity'
        ]
        
        for field in required_fields:
            if field not in event:
                return False, f"Missing required field: {field}"
        
        # Validate severity
        valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if event['severity'] not in valid_severities:
            return False, f"Invalid severity: {event['severity']}"
        
        # Validate event type
        valid_event_types = [
            'IED_EXPLOSION', 'GUNFIRE', 'BURN_PIT_EXPOSURE',
            'TOXIC_SMOKE', 'TRAINING_EXERCISE', 'ROUTINE_PATROL',
            'BLAST_INJURY', 'VEHICLE_ACCIDENT'
        ]
        if event['event_type'] not in valid_event_types:
            return False, f"Invalid event_type: {event['event_type']}"
        
        return True, None
    
    def process_event(self, event):
        """Process and store event to Firestore"""
        try:
            # Validate
            is_valid, error = self.validate_event(event)
            if not is_valid:
                return {'success': False, 'error': error}
            
            soldier_id = event['soldier_id']
            event_id = event['event_id']
            
            # Store to Firestore
            doc_ref = self.db.collection('soldiers').document(soldier_id)\
                             .collection('service_record').document(event_id)
            
            # Prepare event data
            event_data = {
                'event_id': event_id,
                'timestamp': event['timestamp'],
                'location': {
                    'latitude': event['latitude'],
                    'longitude': event['longitude']
                },
                'event_type': event['event_type'],
                'severity': event['severity'],
                'noise_level_db': event.get('noise_level_db'),
                'air_quality_index': event.get('air_quality_index'),
                'device_id': event.get('device_id'),
                'device_type': event.get('device_type'),
                'device_manufacturer': event.get('device_manufacturer'),
                'device_battery_percent': event.get('device_battery_percent'),
                'signal_strength_dbm': event.get('signal_strength_dbm'),
                'processed_at': firestore.SERVER_TIMESTAMP
            }
            
            doc_ref.set(event_data)
            
            print(f"✅ Stored event {event_id} for {soldier_id}")
            
            # Update soldier's last activity
            self.update_soldier_last_activity(soldier_id)
            
            return {'success': True, 'event_id': event_id}
            
        except Exception as e:
            print(f"Error processing event: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_health_alert(self, event):
        """Create health alert for high-severity events"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert_data = {
                'alert_id': alert_id,
                'soldier_id': event['soldier_id'],
                'event_id': event['event_id'],
                'alert_type': 'IMMEDIATE_MEDICAL_EVALUATION',
                'severity': event['severity'],
                'event_type': event['event_type'],
                'message': f"Soldier exposed to {event['event_type']}",
                'location': {
                    'latitude': event['latitude'],
                    'longitude': event['longitude']
                },
                'created_at': firestore.SERVER_TIMESTAMP,
                'resolved': False
            }
            
            # Add specific recommendations based on event type
            if event['event_type'] == 'IED_EXPLOSION':
                alert_data['recommendations'] = [
                    'Immediate hearing test',
                    'TBI screening',
                    'Blast exposure documentation'
                ]
            elif event['event_type'] == 'BURN_PIT_EXPOSURE':
                alert_data['recommendations'] = [
                    'Respiratory function test',
                    'Chest X-ray',
                    'Air quality exposure documentation'
                ]
            elif event['event_type'] == 'BLAST_INJURY':
                alert_data['recommendations'] = [
                    'Immediate TBI screening',
                    'Neurological assessment',
                    'Hearing evaluation',
                    'Document blast parameters'
                ]
            elif event['event_type'] == 'GUNFIRE':
                alert_data['recommendations'] = [
                    'Hearing test',
                    'Document exposure duration',
                    'Check for acoustic trauma'
                ]
            elif event['event_type'] == 'TOXIC_SMOKE':
                alert_data['recommendations'] = [
                    'Respiratory assessment',
                    'Pulmonary function test',
                    'Document exposure type and duration'
                ]
            
            self.db.collection('health_alerts').document(alert_id).set(alert_data)
            
            print(f"🚨 Created health alert {alert_id} for {event['soldier_id']}")
            
        except Exception as e:
            print(f"Error creating alert: {e}")
    
    def update_soldier_last_activity(self, soldier_id):
        """Update soldier's last activity timestamp"""
        try:
            soldier_ref = self.db.collection('soldiers').document(soldier_id)
            soldier_ref.set({
                'soldier_id': soldier_id,
                'last_activity': firestore.SERVER_TIMESTAMP,
                'status': 'ACTIVE'
            }, merge=True)
        except Exception as e:
            print(f"Error updating soldier activity: {e}")
    
    def get_soldier_events(self, soldier_id, limit=None):
        """Retrieve all events for a soldier"""
        try:
            query = self.db.collection('soldiers').document(soldier_id)\
                           .collection('service_record')\
                           .order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            
            events = []
            for doc in docs:
                event = doc.to_dict()
                events.append(event)
            
            return events
            
        except Exception as e:
            print(f"Error fetching soldier events: {e}")
            return []
    
    def get_event_statistics(self, soldier_id):
        """Get aggregated statistics for a soldier's events"""
        try:
            events = self.get_soldier_events(soldier_id)
            
            if not events:
                return None
            
            # Calculate statistics
            total_events = len(events)
            critical_events = sum(1 for e in events if e.get('severity') == 'CRITICAL')
            high_events = sum(1 for e in events if e.get('severity') == 'HIGH')
            
            # Count by event type
            event_type_counts = {}
            for event in events:
                event_type = event.get('event_type')
                event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
            
            # Calculate average noise exposure
            noise_readings = [e.get('noise_level_db') for e in events if e.get('noise_level_db')]
            avg_noise = sum(noise_readings) / len(noise_readings) if noise_readings else 0
            max_noise = max(noise_readings) if noise_readings else 0
            
            # Calculate air quality statistics
            aqi_readings = [e.get('air_quality_index') for e in events if e.get('air_quality_index')]
            max_aqi = max(aqi_readings) if aqi_readings else 0
            avg_aqi = sum(aqi_readings) / len(aqi_readings) if aqi_readings else 0
            
            return {
                'soldier_id': soldier_id,
                'total_events': total_events,
                'critical_events': critical_events,
                'high_events': high_events,
                'event_type_counts': event_type_counts,
                'environmental_exposure': {
                    'avg_noise_db': round(avg_noise, 2),
                    'max_noise_db': round(max_noise, 2),
                    'avg_aqi': round(avg_aqi, 2),
                    'max_aqi': max_aqi
                }
            }
            
        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return None