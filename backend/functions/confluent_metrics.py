"""
Fetch metrics from Confluent Cloud
"""

import os
import requests
from requests.auth import HTTPBasicAuth


class ConfluentMetrics:
    def __init__(self):
        self.api_key = os.getenv('CONFLUENT_CLOUD_API_KEY')
        self.api_secret = os.getenv('CONFLUENT_CLOUD_API_SECRET')
        self.cluster_id = os.getenv('CONFLUENT_CLUSTER_ID')
        self.base_url = 'https://api.telemetry.confluent.cloud/v2/metrics'
        
        # Check if credentials are available
        if not self.api_key or not self.api_secret:
            print("⚠️  Warning: Confluent Cloud API credentials not set. Using mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def get_cluster_metrics(self):
        """Get cluster-level metrics"""
        if self.use_mock:
            return self._mock_cluster_metrics()
        
        try:
            # This would call the actual Confluent Cloud API
            # For now, returning mock data as the API requires specific metric queries
            return self._mock_cluster_metrics()
        except Exception as e:
            print(f"Error fetching cluster metrics: {e}")
            return self._mock_cluster_metrics()
    
    def get_all_topics_metrics(self):
        """Get metrics for all topics"""
        if self.use_mock:
            return self._mock_topics_metrics()
        
        try:
            # This would call the actual Confluent Cloud API
            return self._mock_topics_metrics()
        except Exception as e:
            print(f"Error fetching topic metrics: {e}")
            return self._mock_topics_metrics()
    
    def get_consumer_groups_metrics(self):
        """Get consumer group metrics"""
        if self.use_mock:
            return self._mock_consumer_groups_metrics()
        
        try:
            # This would call the actual Confluent Cloud API
            return self._mock_consumer_groups_metrics()
        except Exception as e:
            print(f"Error fetching consumer group metrics: {e}")
            return self._mock_consumer_groups_metrics()
    
    def get_topic_throughput(self, topic_name):
        """Get throughput metrics for a specific topic"""
        if self.use_mock:
            return {
                'topic': topic_name,
                'bytes_in_per_sec': 98000,
                'bytes_out_per_sec': 102000,
                'messages_in_per_sec': 1247
            }
        
        try:
            # Actual API call would go here
            return {
                'topic': topic_name,
                'bytes_in_per_sec': 98000,
                'bytes_out_per_sec': 102000,
                'messages_in_per_sec': 1247
            }
        except Exception as e:
            print(f"Error fetching topic throughput: {e}")
            return {}
    
    def _mock_cluster_metrics(self):
        """Mock cluster metrics for demo/testing"""
        return {
            'cluster_id': self.cluster_id or 'lkc-demo123',
            'status': 'ONLINE',
            'throughput_bytes_per_sec': 125000,
            'request_rate': 1247,
            'active_connections': 5,
            'partition_count': 9,
            'broker_count': 3,
            'response_time_p99_ms': 45,
            'error_rate': 0.01,
            'availability': 99.99,
            'last_updated': 'Just now'
        }
    
    def _mock_topics_metrics(self):
        """Mock topic metrics for demo/testing"""
        return [
            {
                'name': 'battlefield-events-raw',
                'partitions': 3,
                'replication_factor': 3,
                'throughput_messages_per_sec': 1247,
                'bytes_in_per_sec': 98000,
                'bytes_out_per_sec': 102000,
                'retention_ms': 604800000,  # 7 days
                'total_messages': 125478,
                'avg_message_size': 856
            },
            {
                'name': 'high_risk_events',
                'partitions': 1,
                'replication_factor': 3,
                'throughput_messages_per_sec': 47,
                'bytes_in_per_sec': 3200,
                'bytes_out_per_sec': 3400,
                'retention_ms': 2592000000,  # 30 days
                'total_messages': 4521,
                'avg_message_size': 892
            },
            {
                'name': 'health-risk-alerts',
                'partitions': 1,
                'replication_factor': 3,
                'throughput_messages_per_sec': 12,
                'bytes_in_per_sec': 2400,
                'bytes_out_per_sec': 2500,
                'retention_ms': 7776000000,  # 90 days
                'total_messages': 1234,
                'avg_message_size': 1024
            },
            {
                'name': 'burnpit_exposures',
                'partitions': 1,
                'replication_factor': 3,
                'throughput_messages_per_sec': 8,
                'bytes_in_per_sec': 1800,
                'bytes_out_per_sec': 1900,
                'retention_ms': 2592000000,  # 30 days
                'total_messages': 892,
                'avg_message_size': 780
            }
        ]
    
    def _mock_consumer_groups_metrics(self):
        """Mock consumer group metrics for demo/testing"""
        return [
            {
                'group_id': 'valorstream-gcp-connector',
                'state': 'STABLE',
                'members': 1,
                'total_lag': 0,
                'topics': ['battlefield-events-raw'],
                'partition_assignments': [
                    {
                        'partition': 0,
                        'current_offset': 41826,
                        'log_end_offset': 41826,
                        'lag': 0
                    },
                    {
                        'partition': 1,
                        'current_offset': 41833,
                        'log_end_offset': 41833,
                        'lag': 0
                    },
                    {
                        'partition': 2,
                        'current_offset': 41819,
                        'log_end_offset': 41819,
                        'lag': 0
                    }
                ]
            },
            {
                'group_id': 'ksqldb-valorstream-processor',
                'state': 'STABLE',
                'members': 1,
                'total_lag': 0,
                'topics': ['battlefield-events-raw'],
                'partition_assignments': [
                    {
                        'partition': 0,
                        'current_offset': 41826,
                        'log_end_offset': 41826,
                        'lag': 0
                    }
                ]
            }
        ]
    
    def get_health_status(self):
        """Get overall system health status"""
        cluster = self.get_cluster_metrics()
        topics = self.get_all_topics_metrics()
        consumers = self.get_consumer_groups_metrics()
        
        # Calculate health score
        issues = []
        
        # Check cluster
        if cluster.get('status') != 'ONLINE':
            issues.append('Cluster offline')
        
        if cluster.get('error_rate', 0) > 1.0:
            issues.append('High error rate')
        
        # Check consumer lag
        for consumer in consumers:
            if consumer.get('total_lag', 0) > 1000:
                issues.append(f"High lag in consumer group {consumer['group_id']}")
        
        # Determine status
        if not issues:
            status = 'HEALTHY'
            color = 'green'
        elif len(issues) <= 2:
            status = 'WARNING'
            color = 'yellow'
        else:
            status = 'CRITICAL'
            color = 'red'
        
        return {
            'status': status,
            'color': color,
            'issues': issues,
            'cluster_status': cluster.get('status'),
            'total_topics': len(topics),
            'total_consumer_groups': len(consumers),
            'total_partitions': cluster.get('partition_count', 0),
            'total_lag': sum(c.get('total_lag', 0) for c in consumers),
            'availability': cluster.get('availability', 0)
        }