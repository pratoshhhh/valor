import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_CONFIG = {
    'bootstrap.servers': os.getenv('CONFLUENT_BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('CONFLUENT_API_KEY'),
    'sasl.password': os.getenv('CONFLUENT_API_SECRET'),
}

SCHEMA_REGISTRY_CONFIG = {
    'url': os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('CONFLUENT_SCHEMA_REGISTRY_API_KEY')}:{os.getenv('CONFLUENT_SCHEMA_REGISTRY_API_SECRET')}"
}

GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'valorstream-demo-1')
GCP_REGION = os.getenv('GCP_REGION', 'us-east1')
