# GCP Deployment Guide
## Maasai Mara Wildlife System

---

## Prerequisites

- GCP project `dissertation-498512` with billing enabled
- `gcloud` CLI installed and authenticated (`gcloud auth login`)
- Docker installed
- Your `final_app/` folder with all code
- `secrets/gcp-key.json` in place

---

## Step 0 — One-time IAM setup

Run this once to create the service account with correct permissions:

```bash
cd deployment/
chmod +x setup_iam.sh
./setup_iam.sh
```

This creates a `wildlife-api-sa` service account with:
- `storage.objectViewer` — read model and vectorstore from GCS
- `bigquery.dataEditor` — write query logs to BigQuery
- `secretmanager.secretAccessor` — read Gemini API key from Secret Manager

---

## Step 1 — Set environment variables

```bash
export PROJECT_ID="dissertation-498512"
export BUCKET_NAME="animals-dataset-dissertation"
export GEMINI_API_KEY="your-gemini-api-key-here"
```

---

## Step 2 — Run deployment script

```bash
cd final_app/
cp ../deployment/schema.json .
chmod +x ../deployment/deploy.sh
../deployment/deploy.sh
```

This script will:
1. Enable all required GCP APIs
2. Build and push Docker images to Container Registry
3. Store Gemini API key in Secret Manager
4. Create BigQuery dataset and table
5. Deploy API to Cloud Run (europe-west2, 4GB RAM, 2 CPU)
6. Deploy Frontend to Cloud Run
7. Print both public URLs

---

## Step 3 — Verify deployment

```bash
# Check API health
curl https://your-api-url.run.app/health

# Expected response:
# {"status":"ok","cnn_loaded":true,"rag_loaded":true,"yolo_loaded":true}
```

Then open your frontend URL in a browser.

---

## BigQuery — Query your logs

After a few test queries, open the BigQuery console and run:

```sql
-- Most common species detected
SELECT
  d.species,
  COUNT(*) AS detections,
  ROUND(AVG(d.species_conf), 3) AS avg_confidence
FROM `dissertation-498512.wildlife_queries.query_logs`,
UNNEST(detections) AS d
GROUP BY d.species
ORDER BY detections DESC;

-- Average latency over time
SELECT
  DATE(timestamp) AS date,
  ROUND(AVG(latency_ms), 0) AS avg_latency_ms,
  COUNT(*) AS queries
FROM `dissertation-498512.wildlife_queries.query_logs`
GROUP BY date
ORDER BY date;

-- Habitat distribution
SELECT
  habitat,
  COUNT(*) AS count,
  ROUND(AVG(latency_ms), 0) AS avg_latency_ms
FROM `dissertation-498512.wildlife_queries.query_logs`
GROUP BY habitat
ORDER BY count DESC;

-- YOLO fallback rate (how often YOLO found nothing)
SELECT
  COUNTIF(yolo_fallback) AS fallback_count,
  COUNT(*) AS total,
  ROUND(COUNTIF(yolo_fallback) / COUNT(*) * 100, 1) AS fallback_pct
FROM `dissertation-498512.wildlife_queries.query_logs`;

-- Most cited sources
SELECT
  s.source_name,
  COUNT(*) AS times_cited
FROM `dissertation-498512.wildlife_queries.query_logs`,
UNNEST(sources) AS s
GROUP BY s.source_name
ORDER BY times_cited DESC;

-- Questions asked about dangerous species
SELECT question, answer, timestamp
FROM `dissertation-498512.wildlife_queries.query_logs`
WHERE LOWER(question) LIKE '%dangerous%'
ORDER BY timestamp DESC
LIMIT 20;
```

---

## Cloud Run settings explained

| Setting | Value | Reason |
|---|---|---|
| Memory (API) | 4Gi | TF + YOLO + embeddings all in RAM |
| CPU (API) | 2 | Inference is CPU-bound without GPU |
| Timeout | 120s | Model inference can be slow on first request |
| Min instances | 0 | Saves cost — scales to zero when idle |
| Max instances | 3 | Prevents runaway costs |
| Concurrency | 10 | One instance handles up to 10 concurrent requests |
| Region | europe-west2 | Closest to Glasgow, lowest latency |

---

## Cost estimate (student usage)

| Service | Estimated monthly cost |
|---|---|
| Cloud Run (API) | ~£3-8 (pay per request) |
| Cloud Run (Frontend) | ~£1-2 |
| Cloud Storage | ~£0.50 |
| BigQuery | Free tier (10GB storage, 1TB queries/month) |
| Secret Manager | ~£0.05 |
| **Total** | **~£5-11/month** |

Apply for GCP research credits at cloud.google.com/edu to cover this.

---

## Updating after code changes

```bash
# Rebuild and redeploy API only
docker build -t gcr.io/dissertation-498512/maasai-mara-api ./app
docker push gcr.io/dissertation-498512/maasai-mara-api
gcloud run deploy maasai-mara-api \
  --image gcr.io/dissertation-498512/maasai-mara-api \
  --region europe-west2

# Rebuild and redeploy frontend only
docker build -t gcr.io/dissertation-498512/maasai-mara-frontend ./frontend
docker push gcr.io/dissertation-498512/maasai-mara-frontend
gcloud run deploy maasai-mara-frontend \
  --image gcr.io/dissertation-498512/maasai-mara-frontend \
  --region europe-west2
```
