#!/usr/bin/env python3
"""
Initialize Firestore with sample soldier data
"""

from google.cloud import firestore
from datetime import datetime, timedelta
import random
import uuid

# Initialize Firestore
db = firestore.Client(project='valorstream-demo-1')

def create_soldiers():
    """Create sample soldier records"""
    soldiers = [
        {
            'soldier_id': 'SGT_JOHNSON_001',
            'name': 'Michael Johnson',
            'rank': 'Sergeant',
            'unit': '1st Battalion, 5th Marines',
            'deployment_location': 'Forward Operating Base Delta',
            'deployment_start': '2024-06-15',
            'status': 'active',
            'health_score': 87,
            'vitals': {
                'heart_rate': 78,
                'temperature': 98.6,
                'oxygen': 98,
                'blood_pressure': '120/80'
            }
        },
        {
            'soldier_id': 'CPL_MARTINEZ_002',
            'name': 'Carlos Martinez',
            'rank': 'Corporal',
            'unit': '2nd Battalion, 7th Infantry',
            'deployment_location': 'Camp Phoenix',
            'deployment_start': '2024-08-20',
            'status': 'active',
            'health_score': 92,
            'vitals': {
                'heart_rate': 72,
                'temperature': 98.4,
                'oxygen': 99,
                'blood_pressure': '118/76'
            }
        },
        {
            'soldier_id': 'PFC_WILLIAMS_003',
            'name': 'Sarah Williams',
            'rank': 'Private First Class',
            'unit': '3rd Battalion, 1st Marines',
            'deployment_location': 'Base Medical',
            'deployment_start': '2024-05-10',
            'status': 'medical',
            'health_score': 64,
            'vitals': {
                'heart_rate': 88,
                'temperature': 99.2,
                'oxygen': 95,
                'blood_pressure': '135/88'
            }
        },
        {
            'soldier_id': 'SFC_DAVIS_004',
            'name': 'Robert Davis',
            'rank': 'Sergeant First Class',
            'unit': '1st Special Forces Group',
            'deployment_location': 'Training Ground Charlie',
            'deployment_start': '2024-03-01',
            'status': 'active',
            'health_score': 95,
            'vitals': {
                'heart_rate': 68,
                'temperature': 98.2,
                'oxygen': 99,
                'blood_pressure': '115/72'
            }
        },
        {
            'soldier_id': 'SGT_BROWN_005',
            'name': 'Jennifer Brown',
            'rank': 'Sergeant',
            'unit': '82nd Airborne Division',
            'deployment_location': 'Patrol Route 7',
            'deployment_start': '2024-07-12',
            'status': 'active',
            'health_score': 78,
            'vitals': {
                'heart_rate': 82,
                'temperature': 98.8,
                'oxygen': 97,
                'blood_pressure': '125/82'
            }
        }
    ]
    
    print("📝 Creating soldier records...")
    for soldier in soldiers:
        doc_ref = db.collection('soldiers').document(soldier['soldier_id'])
        doc_ref.set(soldier)
        print(f"  ✅ Created: {soldier['soldier_id']} - {soldier['name']}")
    
    print(f"\n✅ Created {len(soldiers)} soldier records")

def create_health_alerts():
    """Create sample health alerts"""
    alerts = [
        {
            'event_id': str(uuid.uuid4()),
            'soldier_id': 'SGT_JOHNSON_001',
            'event_type': 'Heat Stress',
            'severity': 'HIGH',
            'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            'location': 'Forward Operating Base Delta',
            'status': 'pending',
            'details': {
                'core_temperature': 102.3,
                'description': 'Elevated core temperature during patrol'
            }
        },
        {
            'event_id': str(uuid.uuid4()),
            'soldier_id': 'SGT_JOHNSON_001',
            'event_type': 'Burn Pit Exposure',
            'severity': 'MEDIUM',
            'timestamp': (datetime.utcnow() - timedelta(days=1)).isoformat(),
            'location': 'Waste Disposal Area',
            'status': 'pending',
            'details': {
                'pm25_level': 187,
                'exposure_duration': '45 minutes',
                'description': 'Detected near burn pit zone'
            }
        },
        {
            'event_id': str(uuid.uuid4()),
            'soldier_id': 'PFC_WILLIAMS_003',
            'event_type': 'Cardiac Irregularity',
            'severity': 'CRITICAL',
            'timestamp': (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
            'location': 'Base Medical',
            'status': 'pending',
            'details': {
                'heart_rate': 145,
                'irregularity_type': 'Tachycardia',
                'description': 'Abnormal heart rhythm detected'
            }
        },
        {
            'event_id': str(uuid.uuid4()),
            'soldier_id': 'SGT_BROWN_005',
            'event_type': 'Respiratory Alert',
            'severity': 'HIGH',
            'timestamp': (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            'location': 'Patrol Route 7',
            'status': 'pending',
            'details': {
                'oxygen_saturation': 94,
                'respiratory_rate': 28,
                'description': 'Low oxygen saturation detected'
            }
        },
        {
            'event_id': str(uuid.uuid4()),
            'soldier_id': 'CPL_MARTINEZ_002',
            'event_type': 'Environmental Hazard',
            'severity': 'MEDIUM',
            'timestamp': (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            'location': 'Camp Phoenix',
            'status': 'resolved',
            'details': {
                'hazard_type': 'High particulate matter',
                'pm25_level': 156,
                'description': 'Sandstorm exposure'
            }
        }
    ]
    
    print("\n🚨 Creating health alerts...")
    for alert in alerts:
        doc_ref = db.collection('health_alerts').document(alert['event_id'])
        doc_ref.set(alert)
        severity_icon = '🔴' if alert['severity'] == 'CRITICAL' else '🟠' if alert['severity'] == 'HIGH' else '🟡'
        print(f"  {severity_icon} Created: {alert['event_type']} - {alert['soldier_id']}")
    
    print(f"\n✅ Created {len(alerts)} health alerts")

def main():
    print("=" * 70)
    print("🚀 Initializing VALOR Firestore Database")
    print("=" * 70)
    print()
    
    # Create collections
    create_soldiers()
    create_health_alerts()
    
    print()
    print("=" * 70)
    print("✅ Database initialization complete!")
    print("=" * 70)
    print()
    print("📊 Collections created:")
    print("  - soldiers: 5 records")
    print("  - health_alerts: 5 records")
    print()
    print("🎯 Next steps:")
    print("  1. Start the producer: python producer.py")
    print("  2. Start the consumer: python consumer.py")
    print("  3. Refresh your dashboard")

if __name__ == '__main__':
    main()