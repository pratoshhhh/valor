from producers.producer import BattlefieldEventProducer
import time

def stress_test(num_soldiers=50, events_per_soldier=100):
    """Generate load to test throughput"""
    producer = BattlefieldEventProducer()
    
    start_time = time.time()
    total_events = 0
    
    print(f"🔥 Starting load test: {num_soldiers} soldiers, {events_per_soldier} events each")
    
    for i in range(num_soldiers):
        soldier_id = f"SOLDIER_{i:04d}"
        
        for j in range(events_per_soldier):
            event = producer.generate_event(soldier_id, deployment_day=1)
            producer.send_event(event)
            total_events += 1
            
            if total_events % 100 == 0:
                print(f"Sent {total_events} events...")
    
    producer.producer.flush()
    
    elapsed = time.time() - start_time
    throughput = total_events / elapsed
    
    print(f"\n✅ Load test complete:")
    print(f"   Total events: {total_events}")
    print(f"   Time elapsed: {elapsed:.2f}s")
    print(f"   Throughput: {throughput:.2f} events/sec")

if __name__ == "__main__":
    stress_test(num_soldiers=10, events_per_soldier=50)
