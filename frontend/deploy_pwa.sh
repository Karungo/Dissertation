#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Deploy PWA frontend to GCP Cloud Run
# Run from the pwa_frontend/ directory
# ─────────────────────────────────────────────────────────────────────────────
set -e

PROJECT_ID="dissertation-498512"
REGION="europe-west2"
IMAGE="gcr.io/$PROJECT_ID/maasai-mara-pwa"
SERVICE="maasai-mara-pwa"

# Your deployed API URL — update this after deploying the backend
API_URL="${API_URL:-https://maasai-mara-api-XXXX-ew.a.run.app}"

echo "=== Building PWA image ==="
docker build -t $IMAGE .
docker push $IMAGE

echo "=== Deploying to Cloud Run ==="
gcloud run deploy $SERVICE \
  --image        $IMAGE \
  --platform     managed \
  --region       $REGION \
  --memory       256Mi \
  --cpu          1 \
  --min-instances 0 \
  --max-instances 5 \
  --allow-unauthenticated

echo "=== Get PWA URL ==="
PWA_URL=$(gcloud run services describe $SERVICE \
  --region $REGION \
  --format "value(status.url)")

echo ""
echo "========================================"
echo "  PWA DEPLOYED"
echo "========================================"
echo "  URL      : $PWA_URL"
echo "  Install  : Visit URL on phone → share → Add to Home Screen"
echo "========================================"
echo ""
echo "IMPORTANT: Update API_URL in index.html:"
echo "  const API_URL = \"$API_URL\";"
echo ""
echo "Then rebuild and redeploy."
