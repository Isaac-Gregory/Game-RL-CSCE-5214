# Deployment Guide

## Prerequisites
- Google Cloud Platform (GCP) account
- Google Cloud SDK installed

## Deployment Steps

### 1. Project Setup in GCP
1. Create a new project in Google Cloud Console
2. Enable these APIs:
   - Compute Engine API
   - Cloud Run API
   - Container Registry API

### 2. Local Deployment
```bash
# Authenticate with GCP
gcloud auth login

# Set project
gcloud config set project Game-RL-CSCE-5214

# Build and deploy container
gcloud builds submit --tag gcr.io/Game-RL-CSCE-5214/connect4

# Deploy to Cloud Run
gcloud run deploy connect4 \
  --image gcr.io/Game-RL-CSCE-5214/connect4 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
