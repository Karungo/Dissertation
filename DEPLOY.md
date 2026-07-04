# Deploying to a GCP Compute Engine VM

This stack has two containers, wired together with `docker-compose.yml`:

- **api** — your existing FastAPI CNN+RAG service (`./app`), port `8080`
- **frontend** — the new Streamlit UI (`./frontend`), port `8501`, which
  talks to `api` over the internal Docker network at `http://api:8080`

## 1. Create the VM

```bash
gcloud compute instances create wildlife-app-vm \
  --zone=europe-west2-b \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --boot-disk-size=30GB \
  --tags=wildlife-app \
  --scopes=storage-ro   # lets the VM's default service account read the GCS bucket
```

Adjust `--machine-type` upward (e.g. `e2-standard-4`) if TensorFlow inference
feels slow — the CNN and sentence-transformer embeddings are CPU-bound.

## 2. Open the firewall for the Streamlit port

Only the frontend needs to be public; keep the API internal if you don't need
to call it directly from outside.

```bash
gcloud compute firewall-rules create allow-streamlit \
  --allow=tcp:8501 \
  --target-tags=wildlife-app \
  --direction=INGRESS \
  --source-ranges=0.0.0.0/0
```

(If you also want to hit the API directly for debugging, add a second rule
for `tcp:8080`.)

## 3. SSH in and install Docker + Compose

```bash
gcloud compute ssh wildlife-app-vm --zone=europe-west2-b
```

On the VM:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Run docker without sudo
sudo usermod -aG docker $USER
newgrp docker
```

## 4. Get the code onto the VM

Either `git clone` your repo, or copy it from your machine:

```bash
# from your local machine
gcloud compute scp --recurse ./Dissertation1-master wildlife-app-vm:~/app --zone=europe-west2-b
```

## 5. Provide credentials

Two secrets are needed by the API container:

**a) Gemini API key and bucket name** — create a `.env` file next to
`docker-compose.yml`:

```bash
cd ~/app
cat > .env << 'EOF'
GEMINI_API_KEY=your-gemini-key-here
BUCKET_NAME=animals-dataset-dissertation
EOF
```

**b) GCS service-account key** — `storage.py` uses
`google.cloud.storage.Client()`, which needs credentials to read your model
and FAISS index from the bucket. If the VM's attached service account
already has `storage.objectViewer` on the bucket (via `--scopes=storage-ro`
above, plus an IAM binding), you can skip this and instead delete the
`GOOGLE_APPLICATION_CREDENTIALS` line and the key-file volume mount from
`docker-compose.yml`. Otherwise, drop a key file in:

```bash
mkdir -p secrets
# copy a downloaded service-account JSON key here:
#   gcloud compute scp ./gcp-key.json wildlife-app-vm:~/app/secrets/gcp-key.json
```

## 6. Build and run

```bash
cd ~/app/Dissertation1-master
docker compose up -d --build
```

Check status:

```bash
docker compose ps
docker compose logs -f api
docker compose logs -f frontend
```

## 7. Open the app

Find the VM's external IP:

```bash
gcloud compute instances describe wildlife-app-vm \
  --zone=europe-west2-b \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

Visit `http://<EXTERNAL_IP>:8501` in your browser.

## Notes / production hardening

- **First boot is slow**: `startup()` downloads the Keras model and FAISS
  index from GCS on first request/startup and caches them under `/tmp`
  inside the container. That cache is lost on `docker compose down`/restart
  unless you mount a volume for `/tmp/models` and `/tmp/vectorstore`.
- **Restarting containers**: `docker compose restart` keeps volumes/cache;
  `docker compose down` + `up` removes the containers (and their `/tmp`
  cache) but not named volumes.
- **HTTPS**: put Nginx or Caddy in front of Streamlit (or use a GCP HTTPS
  load balancer) if you need TLS — Streamlit itself serves plain HTTP.
- **Static IP**: reserve one with `gcloud compute addresses create` so the
  URL doesn't change on VM restart.
- **Auto-start on reboot**: `docker compose` services with
  `restart: unless-stopped` (already set) will come back up automatically
  after a VM reboot, as long as the Docker daemon itself is enabled
  (`sudo systemctl enable docker`).
