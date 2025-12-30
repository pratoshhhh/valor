#!/bin/bash

# ValorStream GCP Setup Script
# Automates the setup of Google Cloud Platform resources

set -e  # Exit on any error

PROJECT_ID="valorstream-demo-1"
REGION="us-east1"
BUCKET_NAME="valorstream-reports"

echo "🔵 Setting up Google Cloud Platform for ValorStream..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📌 Setting active project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
echo "   This may take 2-3 minutes..."
gcloud services enable \
    cloudfunctions.googleapis.com \
    run.googleapis.com \
    firestore.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    --quiet

echo "✅ APIs enabled"

# Check if Firestore database exists
echo ""
echo "🗄️  Checking Firestore database..."
FIRESTORE_EXISTS=$(gcloud firestore databases list --format="value(name)" 2>/dev/null | grep -c "(default)" || echo "0")

if [ "$FIRESTORE_EXISTS" -eq "0" ]; then
    echo "Creating Firestore database in $REGION..."
    gcloud firestore databases create --location=$REGION --type=firestore-native
    echo "✅ Firestore database created"
else
    echo "✅ Firestore database already exists"
fi

# Create Cloud Storage bucket for reports
echo ""
echo "📦 Creating Cloud Storage bucket for VA reports..."
BUCKET_EXISTS=$(gsutil ls -b gs://$BUCKET_NAME 2>/dev/null | grep -c "$BUCKET_NAME" || echo "0")

if [ "$BUCKET_EXISTS" -eq "0" ]; then
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo "✅ Storage bucket created: gs://$BUCKET_NAME"
else
    echo "✅ Storage bucket already exists: gs://$BUCKET_NAME"
fi

# Make bucket publicly readable (for demo - use signed URLs in production)
echo "🔓 Setting bucket permissions (public read for demo)..."
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME || echo "⚠️  Warning: Could not set public access"

# Set up Application Default Credentials
echo ""
echo "🔑 Checking authentication..."
if gcloud auth application-default print-access-token &> /dev/null; then
    echo "✅ Application Default Credentials are set"
else
    echo "⚠️  Application Default Credentials not found"
    echo "   Run: gcloud auth application-default login"
fi

# Display environment variables needed
echo ""
echo "="*70
echo "✅ GCP SETUP COMPLETE!"
echo "="*70
echo ""
echo "📝 Add these to your config/.env file:"
echo ""
echo "GCP_PROJECT_ID=$PROJECT_ID"
echo "GCP_REGION=$REGION"
echo "GCS_BUCKET_NAME=$BUCKET_NAME"
echo ""
echo "Next steps:"
echo "1. Run: gcloud auth application-default login (if not done)"
echo "2. Update config/.env with the values above"
echo "3. Run: ./setup_confluent.sh"
echo ""