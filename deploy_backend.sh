#!/bin/bash

echo "🚀 Deploying PHY64ALL Backend to Cloud Run..."

# Get project ID
export PROJECT_ID=$(gcloud config get-value project)
echo "📋 Project ID: $PROJECT_ID"

# Build the container
echo "📦 Building container image..."
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/phy64all-backend:v1

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy phy64all-backend \
  --image gcr.io/$PROJECT_ID/phy64all-backend:v1 \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated \
  --set-secrets="GEMINI_API_KEY=GEMINI_API_KEY:latest" \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-env-vars="PROJECT_NAME=PHY64ALL" \
  --set-env-vars="ENVIRONMENT=production" \
  --memory=1Gi \
  --cpu=1 \
  --max-instances=10 \
  --min-instances=0 \
  --concurrency=80 \
  --timeout=300

# Get the backend URL
BACKEND_URL=$(gcloud run services describe phy64all-backend --region asia-south1 --format="value(status.url)")
echo "✅ Backend deployed successfully!"
echo "🔗 Backend URL: $BACKEND_URL"

# Save URL for frontend
echo "BACKEND_URL=$BACKEND_URL" > ../frontend/.env
echo "✅ Backend URL saved to frontend/.env"

cd ..
