FROM python:3.12-slim

# System libraries needed by TensorFlow and Pillow
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (layer cached unless requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Add /app to PYTHONPATH so all module imports resolve correctly
ENV PYTHONPATH=/app

EXPOSE 8080

# Environment variables — override at runtime
ENV BUCKET_NAME=""
ENV GEMINI_API_KEY=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
