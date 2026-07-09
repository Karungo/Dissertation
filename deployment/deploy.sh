#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Maasai Mara Wildlife System — Full GCP Deployment
# Deploys: FastAPI backend + PWA frontend to Cloud Run
# Run from the final_app/ directory
# ─────────────────────────────────────────────────────────────────────────────
set -e

PROJECT_ID="dissertation-498512"
REGION="europe-west2"
API_IMAGE="gcr.io/$PROJECT_ID/maasai-mara-api"
PWA_IMAGE="gcr.io/$PROJECT_ID/maasai-mara-pwa"
API_SERVICE="maasai-mara-api"
PWA_SERVICE="maasai-mara-pwa"

echo ""
echo "======================================================"
echo "  Maasai Mara Wildlife System — GCP Deployment"
echo "======================================================"

# ── Pre-flight checks ──────────────────────────────────────────────
if [ -z "$BUCKET_NAME" ]; then
  echo "ERROR: BUCKET_NAME is not set."
  echo "Run: export BUCKET_NAME=animals-dataset-dissertation"
  exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
  echo "ERROR: GEMINI_API_KEY is not set."
  echo "Run: export GEMINI_API_KEY=your-key-here"
  exit 1
fi

echo ""
echo "Project  : $PROJECT_ID"
echo "Region   : $REGION"
echo "Bucket   : $BUCKET_NAME"
echo ""

# ── Step 1: Set project ────────────────────────────────────────────
echo "=== Step 1/10: Set GCP project ==="
gcloud config set project $PROJECT_ID

# ── Step 2: Enable APIs ────────────────────────────────────────────
echo "=== Step 2/10: Enable required GCP APIs ==="
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com

# ── Step 3: Docker auth ────────────────────────────────────────────
echo "=== Step 3/10: Configure Docker auth ==="
gcloud auth configure-docker --quiet

# ── Step 4: Build and push API ─────────────────────────────────────
echo "=== Step 4/10: Build and push API image ==="
docker build -t $API_IMAGE ./app
docker push $API_IMAGE
echo "API image pushed: $API_IMAGE"

# ── Step 5: Build and push PWA ─────────────────────────────────────
echo "=== Step 5/10: Build and push PWA image ==="
docker build -t $PWA_IMAGE ./pwa_frontend
docker push $PWA_IMAGE
echo "PWA image pushed: $PWA_IMAGE"

# ── Step 6: Store Gemini API key in Secret Manager ─────────────────
echo "=== Step 6/10: Store Gemini API key in Secret Manager ==="
echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key \
  --data-file=- \
  --replication-policy=automatic 2>/dev/null || \
echo -n "$GEMINI_API_KEY" | gcloud secrets versions add gemini-api-key \
  --data-file=-
echo "Secret stored."

# ── Step 7: Create BigQuery dataset and table ──────────────────────
echo "=== Step 7/10: Create BigQuery dataset and table ==="
bq mk \
  --dataset \
  --location=$REGION \
  --description="Maasai Mara Wildlife Query Logs" \
  $PROJECT_ID:wildlife_queries 2>/dev/null || echo "Dataset already exists."

bq mk \
  --table \
  $PROJECT_ID:wildlife_queries.query_logs \
  schema.json 2>/dev/null || echo "Table already exists."

# ── Step 8: Deploy API to Cloud Run ───────────────────────────────
echo "=== Step 8/10: Deploy API to Cloud Run ==="
gcloud run deploy $API_SERVICE \
  --image             $API_IMAGE \
  --platform          managed \
  --region            $REGION \
  --memory            4Gi \
  --cpu               2 \
  --timeout           120 \
  --concurrency       10 \
  --min-instances     0 \
  --max-instances     3 \
  --set-env-vars      BUCKET_NAME=$BUCKET_NAME \
  --set-secrets       GEMINI_API_KEY=gemini-api-key:latest \
  --service-account   wildlife-api-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --allow-unauthenticated

# ── Step 9: Get API URL ────────────────────────────────────────────
echo "=== Step 9/10: Getting API URL ==="
API_URL=$(gcloud run services describe $API_SERVICE \
  --region $REGION \
  --format "value(status.url)")
echo "API URL: $API_URL"

# ── Inject API URL into PWA before deploying ──────────────────────
# This patches index.html so the PWA points to the real API
sed -i "s|https://your-api-url.run.app|$API_URL|g" ./pwa_frontend/index.html
echo "API URL injected into PWA."

# Rebuild PWA image with correct API URL baked in
docker build -t $PWA_IMAGE ./pwa_frontend
docker push $PWA_IMAGE

# ── Step 10: Deploy PWA to Cloud Run ─────────────────────────────
echo "=== Step 10/10: Deploy PWA to Cloud Run ==="
gcloud run deploy $PWA_SERVICE \
  --image             $PWA_IMAGE \
  --platform          managed \
  --region            $REGION \
  --memory            256Mi \
  --cpu               1 \
  --min-instances     0 \
  --max-instances     5 \
  --allow-unauthenticated

PWA_URL=$(gcloud run services describe $PWA_SERVICE \
  --region $REGION \
  --format "value(status.url)")

# ── Summary ────────────────────────────────────────────────────────
echo ""
echo "======================================================"
echo "  DEPLOYMENT COMPLETE"
echo "======================================================"
echo ""
echo "  API          : $API_URL"
echo "  API Docs     : $API_URL/docs"
echo "  API Health   : $API_URL/health"
echo ""
echo "  PWA Frontend : $PWA_URL"
echo ""
echo "  Install on phone:"
echo "  Android → Chrome → three-dot menu → Add to Home Screen"
echo "  iPhone  → Safari → Share → Add to Home Screen"
echo ""
echo "  BigQuery logs:"
echo "  https://console.cloud.google.com/bigquery?project=$PROJECT_ID"
echo "======================================================"
