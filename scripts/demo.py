import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from producers.producer import BattlefieldEventProducer

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_demo():
    print_header("🎖️  VALORSTREAM: Real-Time Legacy & Care")
    print("This demo shows the complete pipeline:")
    print("  1. Battlefield IoT sensors generating data")
    print("  2. Real-time streaming through Confluent Cloud")
    print("  3. AI analysis with Google Vertex AI")
    print("  4. Automatic VA report generation\n")
    
    input("Press ENTER to begin...")
    
    print_header("🚁 DEPLOYMENT SIMULATION")
    producer = BattlefieldEventProducer()
    producer.simulate_deployment("SGT_JOHNSON_001", duration_hours=1, events_per_hour=10)
    
    print_header("✅ DEMO COMPLETE")
    print("\n  Every event is now:")
    print("  📊 Stored in Confluent Cloud")
    print("  ⚡ Processed by ksqlDB")
    print("  💾 Saved to Firestore")
    print("  🤖 Ready for AI analysis\n")

if __name__ == "__main__":
    run_demo()
