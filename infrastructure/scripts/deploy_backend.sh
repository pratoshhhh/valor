#!/bin/bash

# ValorStream Backend Deployment Script
# Deploys Cloud Functions to Google Cloud Platform

set -e  # Exit on any error

PROJECT_ID="valorstream-demo-1"
REGION="us-east1"
BACKEND_DIR="backend/functions"

echo "🚀 Deploying ValorStream Backend to Google Cloud Functions..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    exit 1
fi

# Set project
gcloud config set project $PROJECT_ID

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: Backend directory not found: $BACKEND_DIR"
    echo "   Make sure you're running this from the project root"
    exit 1
fi

# Check for required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set"
    echo "   AI report generation will use mock data"
    echo "   Set it with: export GEMINI_API_KEY=your_key"
    echo ""
fi

# Navigate to backend directory
cd $BACKEND_DIR

echo "📦 Backend files found:"
ls -1 *.py
echo ""

# Deploy Function 1: ingest_events
echo "📤 Deploying ingest_events function..."
gcloud functions deploy ingest-events \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=ingest_events \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=60s \
    --memory=512MB \
    --set-env-vars GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
    --quiet

INGEST_URL=$(gcloud functions describe ingest-events --region=$REGION --gen2 --format="value(serviceConfig.uri)" 2>/dev/null || echo "")
echo "✅ ingest-events deployed"

# Deploy Function 2: generate_va_report
echo ""
echo "📄 Deploying generate_va_report function..."
gcloud functions deploy generate-va-report \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=generate_va_report \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=540s \
    --memory=1024MB \
    --set-env-vars GEMINI_API_KEY="${GEMINI_API_KEY:-}",GCS_BUCKET_NAME="valorstream-reports" \
    --quiet

REPORT_URL=$(gcloud functions describe generate-va-report --region=$REGION --gen2 --format="value(serviceConfig.uri)" 2>/dev/null || echo "")
echo "✅ generate-va-report deployed"

# Deploy Function 3: get_confluent_metrics
echo ""
echo "📊 Deploying get_confluent_metrics function..."
gcloud functions deploy get-confluent-metrics \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=get_confluent_metrics \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=30s \
    --memory=256MB \
    --quiet

METRICS_URL=$(gcloud functions describe get-confluent-metrics --region=$REGION --gen2 --format="value(serviceConfig.uri)" 2>/dev/null || echo "")
echo "✅ get-confluent-metrics deployed"

# Deploy Function 4: get_soldier_summary
echo ""
echo "👤 Deploying get_soldier_summary function..."
gcloud functions deploy get-soldier-summary \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=get_soldier_summary \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=30s \
    --memory=256MB \
    --quiet

SUMMARY_URL=$(gcloud functions describe get-soldier-summary --region=$REGION --gen2 --format="value(serviceConfig.uri)" 2>/dev/null || echo "")
echo "✅ get-soldier-summary deployed"

# Deploy Function 5: get_health_alerts
echo ""
echo "🚨 Deploying get_health_alerts function..."
gcloud functions deploy get-health-alerts \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=get_health_alerts \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=30s \
    --memory=256MB \
    --quiet

ALERTS_URL=$(gcloud functions describe get-health-alerts --region=$REGION --gen2 --format="value(serviceConfig.uri)" 2>/dev/null || echo "")
echo "✅ get-health-alerts deployed"

# Deploy Function 6: resolve_alert
echo ""
echo "✔️  Deploying resolve_alert function..."
gcloud functions deploy resolve-alert \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=resolve_alert \
    --trigger-http \
    --allow-unauthenticated \
    --timeout=30s \
    --memory=256MB \
    --quiet

RESOLVE_URL=$(gcloud functions describe resolve-alert --region=$REGION --gen2 --format="value(serviceConfig.uri)" 2>/dev/null || echo "")
echo "✅ resolve-alert deployed"

# Return to project root
cd ../..

# Display all function URLs
echo ""
echo "="*70
echo "✅ ALL CLOUD FUNCTIONS DEPLOYED SUCCESSFULLY!"
echo "="*70
echo ""
echo "🌐 Function URLs:"
echo ""
echo "1. Ingest Events (for Confluent HTTP Sink):"
echo "   $INGEST_URL"
echo ""
echo "2. Generate VA Report:"
echo "   $REPORT_URL"
echo ""
echo "3. Get Confluent Metrics:"
echo "   $METRICS_URL"
echo ""
echo "4. Get Soldier Summary:"
echo "   $SUMMARY_URL"
echo ""
echo "5. Get Health Alerts:"
echo "   $ALERTS_URL"
echo ""
echo "6. Resolve Alert:"
echo "   $RESOLVE_URL"
echo ""
echo "📝 Test the functions:"
echo ""
echo "# Generate VA report for a soldier"
echo "curl -X POST $REPORT_URL \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"soldier_id\": \"SGT_JOHNSON_001\"}'"
echo ""
echo "# Get soldier summary"
echo "curl \"$SUMMARY_URL?soldier_id=SGT_JOHNSON_001\""
echo ""
echo "# Get health alerts"
echo "curl \"$ALERTS_URL\""
echo ""
echo "💡 Next steps:"
echo "1. Configure Confluent HTTP Sink Connector to use the ingest-events URL"
echo "2. Test report generation with your soldier data"
echo "3. Integrate these URLs into your frontend dashboard"
echo ""