import os
from dotenv import load_dotenv
from pathlib import Path

# Get the config directory path
config_dir = Path(__file__).parent
env_path = config_dir / '.env'

# Load .env file
load_dotenv(dotenv_path=env_path)

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

# GCP Configuration - ADD THESE TWO LINES
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'valorstream-demo-1')
GCP_REGION = os.getenv('GCP_REGION', 'us-east1')

# Debug: print to verify loading
if not os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL'):
    print("❌ ERROR: CONFLUENT_SCHEMA_REGISTRY_URL not found in .env")
else:
    print(f"✅ Schema Registry URL loaded: {os.getenv('CONFLUENT_SCHEMA_REGISTRY_URL')}")