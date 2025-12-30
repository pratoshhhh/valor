"""
Firestore write operations utility
Provides consistent interface for writing data to Firestore
"""

from google.cloud import firestore
from datetime import datetime
import uuid


class FirestoreWriter:
    def __init__(self, firestore_client=None):
        """
        Initialize Firestore writer
        
        Args:
            firestore_client: Optional Firestore client. If not provided, creates new one.
        """
        self.db = firestore_client if firestore_client else firestore.Client()
    
    def write_soldier_event(self, soldier_id, event_data):
        """
        Write a battlefield event to a soldier's service record
        
        Args:
            soldier_id: Soldier identifier
            event_data: Dictionary containing event information
            
        Returns:
            Document reference
        """
        try:
            event_id = event_data.get('event_id', str(uuid.uuid4()))
            
            doc_ref = self.db.collection('soldiers').document(soldier_id)\
                             .collection('service_record').document(event_id)
            
            # Ensure timestamp format
            if 'timestamp' in event_data and not isinstance(event_data['timestamp'], int):
                event_data['timestamp'] = int(datetime.now().timestamp() * 1000)
            
            # Add processing metadata
            event_data['processed_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref.set(event_data)
            
            return doc_ref
            
        except Exception as e:
            print(f"Error writing soldier event: {e}")
            raise
    
    def write_health_alert(self, alert_data):
        """
        Write a health alert to Firestore
        
        Args:
            alert_data: Dictionary containing alert information
            
        Returns:
            Document reference
        """
        try:
            alert_id = alert_data.get('alert_id', str(uuid.uuid4()))
            
            doc_ref = self.db.collection('health_alerts').document(alert_id)
            
            # Ensure required fields
            if 'created_at' not in alert_data:
                alert_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            if 'resolved' not in alert_data:
                alert_data['resolved'] = False
            
            doc_ref.set(alert_data)
            
            return doc_ref
            
        except Exception as e:
            print(f"Error writing health alert: {e}")
            raise
    
    def update_soldier_profile(self, soldier_id, profile_data):
        """
        Update or create a soldier's profile
        
        Args:
            soldier_id: Soldier identifier
            profile_data: Dictionary containing profile information
            
        Returns:
            Document reference
        """
        try:
            doc_ref = self.db.collection('soldiers').document(soldier_id)
            
            # Add update timestamp
            profile_data['last_updated'] = firestore.SERVER_TIMESTAMP
            
            # Use merge to not overwrite existing data
            doc_ref.set(profile_data, merge=True)
            
            return doc_ref
            
        except Exception as e:
            print(f"Error updating soldier profile: {e}")
            raise
    
    def write_soldier_summary(self, soldier_id, summary_data):
        """
        Write or update soldier exposure summary
        
        Args:
            soldier_id: Soldier identifier
            summary_data: Dictionary containing summary statistics
            
        Returns:
            Document reference
        """
        try:
            doc_ref = self.db.collection('soldier_summaries').document(soldier_id)
            
            # Add metadata
            summary_data['soldier_id'] = soldier_id
            summary_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref.set(summary_data, merge=True)
            
            return doc_ref
            
        except Exception as e:
            print(f"Error writing soldier summary: {e}")
            raise
    
    def write_va_report_metadata(self, report_id, metadata):
        """
        Write VA report metadata
        
        Args:
            report_id: Report identifier
            metadata: Dictionary containing report metadata
            
        Returns:
            Document reference
        """
        try:
            doc_ref = self.db.collection('va_reports').document(report_id)
            
            # Add generation timestamp
            metadata['generated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref.set(metadata)
            
            return doc_ref
            
        except Exception as e:
            print(f"Error writing VA report metadata: {e}")
            raise
    
    def batch_write_events(self, events_list):
        """
        Write multiple events in a batch operation
        
        Args:
            events_list: List of tuples (soldier_id, event_data)
            
        Returns:
            Number of events written
        """
        try:
            batch = self.db.batch()
            count = 0
            
            for soldier_id, event_data in events_list:
                event_id = event_data.get('event_id', str(uuid.uuid4()))
                
                doc_ref = self.db.collection('soldiers').document(soldier_id)\
                                 .collection('service_record').document(event_id)
                
                event_data['processed_at'] = firestore.SERVER_TIMESTAMP
                batch.set(doc_ref, event_data)
                count += 1
                
                # Commit batch every 500 operations (Firestore limit)
                if count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()
            
            # Commit remaining operations
            if count % 500 != 0:
                batch.commit()
            
            return count
            
        except Exception as e:
            print(f"Error in batch write: {e}")
            raise
    
    def increment_counter(self, counter_name, increment_by=1):
        """
        Increment a counter in Firestore
        
        Args:
            counter_name: Name of the counter
            increment_by: Amount to increment (default 1)
            
        Returns:
            Updated counter value
        """
        try:
            doc_ref = self.db.collection('system_counters').document(counter_name)
            
            doc = doc_ref.get()
            
            if doc.exists:
                current_value = doc.to_dict().get('value', 0)
                new_value = current_value + increment_by
            else:
                new_value = increment_by
            
            doc_ref.set({
                'value': new_value,
                'last_updated': firestore.SERVER_TIMESTAMP
            })
            
            return new_value
            
        except Exception as e:
            print(f"Error incrementing counter: {e}")
            raise
    
    def log_system_event(self, event_type, event_data):
        """
        Log a system event for auditing
        
        Args:
            event_type: Type of system event
            event_data: Dictionary containing event details
            
        Returns:
            Document reference
        """
        try:
            doc_ref = self.db.collection('system_logs').document()
            
            log_entry = {
                'event_type': event_type,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'data': event_data
            }
            
            doc_ref.set(log_entry)
            
            return doc_ref
            
        except Exception as e:
            print(f"Error logging system event: {e}")
            raise
    
    def get_collection_stats(self, collection_name):
        """
        Get statistics about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            
            count = sum(1 for _ in docs)
            
            return {
                'collection': collection_name,
                'document_count': count,
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {
                'collection': collection_name,
                'document_count': 0,
                'error': str(e)
            }
    
    def delete_old_data(self, collection_name, days_old=90):
        """
        Delete data older than specified days
        
        Args:
            collection_name: Name of the collection
            days_old: Delete data older than this many days
            
        Returns:
            Number of documents deleted
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cutoff_timestamp = int(cutoff_date.timestamp() * 1000)
            
            collection_ref = self.db.collection(collection_name)
            query = collection_ref.where('timestamp', '<', cutoff_timestamp)
            
            docs = query.stream()
            deleted_count = 0
            
            batch = self.db.batch()
            for doc in docs:
                batch.delete(doc.reference)
                deleted_count += 1
                
                # Commit batch every 500 operations
                if deleted_count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()
            
            # Commit remaining operations
            if deleted_count % 500 != 0:
                batch.commit()
            
            print(f"Deleted {deleted_count} documents from {collection_name}")
            return deleted_count
            
        except Exception as e:
            print(f"Error deleting old data: {e}")
            raise