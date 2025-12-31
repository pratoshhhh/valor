#!/usr/bin/env python3
"""
Standalone Firestore Inspector
No config imports needed - just checks Firestore directly
"""

from google.cloud import firestore
import json

# CHANGE THIS to your project ID
PROJECT_ID = 'valorstream-demo-1'

print("="*70)
print("🔍 Inspecting Firestore health_alerts Collection")
print("="*70)
print(f"Project: {PROJECT_ID}")
print()

try:
    # Connect to Firestore
    db = firestore.Client(project=PROJECT_ID)
    print("✅ Connected to Firestore")
    
    # Get all alerts
    print("\n📊 Querying health_alerts collection...")
    alerts_ref = db.collection('health_alerts')
    alerts = list(alerts_ref.stream())
    
    print(f"✅ Found {len(alerts)} documents")
    
    if len(alerts) > 0:
        print("\n" + "="*70)
        print("📝 FIRST ALERT - DETAILED VIEW")
        print("="*70)
        
        # Show first alert in detail
        first_alert = alerts[0]
        alert_data = first_alert.to_dict()
        
        print(f"\nDocument ID: {first_alert.id}")
        print(f"\nAll Fields:")
        print("-"*70)
        for key, value in sorted(alert_data.items()):
            value_type = type(value).__name__
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."
            print(f"  {key:20s} = {value_str:50s} [{value_type}]")
        
        print("\n" + "="*70)
        print("📋 ALL ALERTS - SUMMARY")
        print("="*70)
        
        for i, alert in enumerate(alerts, 1):
            data = alert.to_dict()
            
            severity_icon = '🔴' if data.get('severity') == 'CRITICAL' else '🟠' if data.get('severity') == 'HIGH' else '🟡'
            
            print(f"\n{i}. {severity_icon} {data.get('event_type', 'Unknown')}")
            print(f"   ID: {alert.id}")
            print(f"   Soldier: {data.get('soldier_id', 'Unknown')}")
            print(f"   Severity: {data.get('severity', 'Unknown')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"   Created: {data.get('created_at', 'N/A')}")
        
        print("\n" + "="*70)
        print("🔧 CLOUD FUNCTION QUERY HINTS")
        print("="*70)
        
        # Analyze what fields are available
        all_fields = set()
        for alert in alerts:
            all_fields.update(alert.to_dict().keys())
        
        print(f"\nAvailable fields in alerts: {sorted(all_fields)}")
        
        # Check for common query fields
        print("\n✅ Fields for querying:")
        if 'status' in all_fields:
            statuses = [a.to_dict().get('status') for a in alerts]
            print(f"   - status: {set(statuses)}")
        if 'severity' in all_fields:
            severities = [a.to_dict().get('severity') for a in alerts]
            print(f"   - severity: {set(severities)}")
        if 'timestamp' in all_fields:
            print(f"   - timestamp: Available (use for sorting)")
        if 'created_at' in all_fields:
            print(f"   - created_at: Available (use for sorting)")
        
    else:
        print("\n⚠️  NO ALERTS FOUND IN FIRESTORE!")
        print("\nPossible reasons:")
        print("  1. Wrong project ID")
        print("  2. initialize_firestore.py didn't run successfully")
        print("  3. Alerts are in a different collection")
        
        print("\n🔍 Let's check soldiers collection:")
        soldiers_ref = db.collection('soldiers')
        soldiers = list(soldiers_ref.stream())
        print(f"   Soldiers found: {len(soldiers)}")
        
        if len(soldiers) > 0:
            print("\n   ✅ Soldiers exist! Sample:")
            sample = soldiers[0].to_dict()
            print(f"      {sample.get('soldier_id')} - {sample.get('name')}")
            
            print("\n   ⚠️  Alerts should exist too. Check Firestore Console:")
            print(f"   https://console.firebase.google.com/project/{PROJECT_ID}/firestore")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n💡 Make sure:")
    print("  1. GOOGLE_APPLICATION_CREDENTIALS is set")
    print("  2. Service account has Firestore permissions")
    print("  3. Project ID is correct")

print("\n" + "="*70)
print("Done!")
print("="*70)