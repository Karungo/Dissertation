#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# IAM Setup — run this ONCE before deploy.sh
# Creates a service account with the exact permissions needed
# ─────────────────────────────────────────────────────────────────────────────
set -e

PROJECT_ID="dissertation-498512"
SA_NAME="wildlife-api-sa"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

echo "=== Creating service account ==="
gcloud iam service-accounts create $SA_NAME \
  --display-name="Maasai Mara Wildlife API" \
  --project=$PROJECT_ID

echo "=== Granting permissions ==="

# Read from GCS bucket (model + vectorstore)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectViewer"

# Write to BigQuery
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.dataEditor"

# Read secrets from Secret Manager
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor"

echo "=== Service account ready: $SA_EMAIL ==="
