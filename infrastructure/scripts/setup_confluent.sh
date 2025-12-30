#!/bin/bash

# ValorStream Confluent Cloud Setup Script
# Automates the setup of Confluent Cloud resources

set -e  # Exit on any error

ENVIRONMENT_NAME="valorstream-env"
CLUSTER_NAME="battlefield-data-stream"
KSQLDB_NAME="valorstream-processor"
CLOUD_PROVIDER="gcp"
REGION="us-east1"

echo "🟠 Setting up Confluent Cloud for ValorStream..."
echo ""

# Check if confluent CLI is installed
if ! command -v confluent &> /dev/null; then
    echo "❌ Error: Confluent CLI is not installed"
    echo "Install from: https://docs.confluent.io/confluent-cli/current/install.html"
    echo ""
    echo "Run: curl -sL --http1.1 https://cnfl.io/cli | sh -s -- latest"
    exit 1
fi

# Login to Confluent Cloud
echo "🔐 Logging in to Confluent Cloud..."
confluent login --save

# List existing environments
echo ""
echo "📋 Checking for existing environments..."
ENV_ID=$(confluent environment list -o json 2>/dev/null | jq -r ".[] | select(.name==\"$ENVIRONMENT_NAME\") | .id" || echo "")

if [ -z "$ENV_ID" ]; then
    echo "Creating environment: $ENVIRONMENT_NAME..."
    confluent environment create $ENVIRONMENT_NAME -o json > /tmp/env_output.json
    ENV_ID=$(jq -r '.id' /tmp/env_output.json)
    echo "✅ Environment created: $ENV_ID"
else
    echo "✅ Environment already exists: $ENV_ID"
fi

# Use the environment
confluent environment use $ENV_ID

# Check for existing Kafka cluster
echo ""
echo "🔍 Checking for existing Kafka cluster..."
CLUSTER_ID=$(confluent kafka cluster list -o json 2>/dev/null | jq -r ".[] | select(.name==\"$CLUSTER_NAME\") | .id" || echo "")

if [ -z "$CLUSTER_ID" ]; then
    echo "⚠️  No cluster found with name: $CLUSTER_NAME"
    echo ""
    echo "Creating Kafka cluster (this takes 3-5 minutes)..."
    confluent kafka cluster create $CLUSTER_NAME \
        --cloud $CLOUD_PROVIDER \
        --region $REGION \
        --type basic \
        -o json > /tmp/cluster_output.json
    
    CLUSTER_ID=$(jq -r '.id' /tmp/cluster_output.json)
    echo "✅ Cluster created: $CLUSTER_ID"
    
    # Wait for cluster to be ready
    echo "⏳ Waiting for cluster to provision..."
    sleep 30
else
    echo "✅ Cluster already exists: $CLUSTER_ID"
fi

# Use the cluster
confluent kafka cluster use $CLUSTER_ID

# Create API keys for Kafka cluster
echo ""
echo "🔑 Creating API keys for Kafka cluster..."
confluent api-key create --resource $CLUSTER_ID -o json > /tmp/kafka_api_key.json
KAFKA_API_KEY=$(jq -r '.api_key' /tmp/kafka_api_key.json)
KAFKA_API_SECRET=$(jq -r '.api_secret' /tmp/kafka_api_key.json)
echo "✅ Kafka API key created"

# Get bootstrap server
BOOTSTRAP_SERVER=$(confluent kafka cluster describe $CLUSTER_ID -o json | jq -r '.endpoint' | sed 's|SASL_SSL://||')

# Create topics
echo ""
echo "📝 Creating Kafka topics..."

# Topic 1: battlefield-events-raw
if confluent kafka topic list | grep -q "battlefield-events-raw"; then
    echo "✅ Topic already exists: battlefield-events-raw"
else
    confluent kafka topic create battlefield-events-raw \
        --partitions 3 \
        --config retention.ms=604800000
    echo "✅ Created topic: battlefield-events-raw"
fi

# Topic 2: health-risk-alerts
if confluent kafka topic list | grep -q "health-risk-alerts"; then
    echo "✅ Topic already exists: health-risk-alerts"
else
    confluent kafka topic create health-risk-alerts \
        --partitions 1 \
        --config retention.ms=7776000000
    echo "✅ Created topic: health-risk-alerts"
fi

# Enable Schema Registry
echo ""
echo "📋 Checking Schema Registry..."
SR_ENDPOINT=$(confluent schema-registry cluster describe -o json 2>/dev/null | jq -r '.endpoint_url' || echo "")

if [ -z "$SR_ENDPOINT" ] || [ "$SR_ENDPOINT" == "null" ]; then
    echo "Enabling Schema Registry..."
    confluent schema-registry cluster enable --cloud $CLOUD_PROVIDER --geo us
    sleep 10
    SR_ENDPOINT=$(confluent schema-registry cluster describe -o json | jq -r '.endpoint_url')
    echo "✅ Schema Registry enabled: $SR_ENDPOINT"
else
    echo "✅ Schema Registry already enabled: $SR_ENDPOINT"
fi

# Create Schema Registry API keys
echo ""
echo "🔑 Creating Schema Registry API keys..."
SR_CLUSTER_ID=$(confluent schema-registry cluster describe -o json | jq -r '.cluster_id')
confluent api-key create --resource $SR_CLUSTER_ID -o json > /tmp/sr_api_key.json
SR_API_KEY=$(jq -r '.api_key' /tmp/sr_api_key.json)
SR_API_SECRET=$(jq -r '.api_secret' /tmp/sr_api_key.json)
echo "✅ Schema Registry API key created"

# Create ksqlDB cluster
echo ""
echo "🔍 Checking for ksqlDB cluster..."
KSQLDB_ID=$(confluent ksql cluster list -o json 2>/dev/null | jq -r ".[] | select(.name==\"$KSQLDB_NAME\") | .id" || echo "")

if [ -z "$KSQLDB_ID" ]; then
    echo "Creating ksqlDB cluster (this takes 3-5 minutes)..."
    confluent ksql cluster create $KSQLDB_NAME \
        --cluster $CLUSTER_ID \
        --csu 1 \
        -o json > /tmp/ksqldb_output.json
    
    KSQLDB_ID=$(jq -r '.id' /tmp/ksqldb_output.json)
    echo "✅ ksqlDB cluster created: $KSQLDB_ID"
else
    echo "✅ ksqlDB cluster already exists: $KSQLDB_ID"
fi

# Display all configuration
echo ""
echo "="*70
echo "✅ CONFLUENT CLOUD SETUP COMPLETE!"
echo "="*70
echo ""
echo "📝 Add these to your config/.env file:"
echo ""
echo "# Kafka Cluster"
echo "CONFLUENT_BOOTSTRAP_SERVERS=$BOOTSTRAP_SERVER"
echo "CONFLUENT_API_KEY=$KAFKA_API_KEY"
echo "CONFLUENT_API_SECRET=$KAFKA_API_SECRET"
echo "CONFLUENT_CLUSTER_ID=$CLUSTER_ID"
echo ""
echo "# Schema Registry"
echo "CONFLUENT_SCHEMA_REGISTRY_URL=$SR_ENDPOINT"
echo "CONFLUENT_SCHEMA_REGISTRY_API_KEY=$SR_API_KEY"
echo "CONFLUENT_SCHEMA_REGISTRY_API_SECRET=$SR_API_SECRET"
echo ""
echo "# ksqlDB"
echo "KSQLDB_CLUSTER_ID=$KSQLDB_ID"
echo ""
echo "⚠️  IMPORTANT: Save these credentials! You cannot view the secrets again."
echo ""
echo "Next steps:"
echo "1. Update config/.env with the values above"
echo "2. Upload your Avro schema to Schema Registry"
echo "3. Run your producer: python3 producers/producer.py"
echo ""

# Clean up temp files
rm -f /tmp/env_output.json /tmp/cluster_output.json /tmp/kafka_api_key.json /tmp/sr_api_key.json /tmp/ksqldb_output.json