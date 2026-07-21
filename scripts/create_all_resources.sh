#!/bin/bash
# ==============================================================================
# Script to provision GCP Test Resources across all governed services
# Project: payments-dev-1
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
NETWORK="default"
PREFIX="test-gov"

echo "Setting project to $PROJECT..."
gcloud config set project $PROJECT

echo "Ensuring required APIs are enabled (This may take a moment)..."
gcloud services enable compute.googleapis.com bigquery.googleapis.com storage.googleapis.com cloudkms.googleapis.com cloudresourcemanager.googleapis.com secretmanager.googleapis.com pubsub.googleapis.com artifactregistry.googleapis.com run.googleapis.com sqladmin.googleapis.com container.googleapis.com redis.googleapis.com aiplatform.googleapis.com dataplex.googleapis.com

# ------------------------------------------------------------------------------
# FAST RESOURCES (Complete instantly)
# ------------------------------------------------------------------------------
echo "Creating Storage Bucket..."
gcloud storage buckets create gs://payments-dev-1-governance-test-bucket --project=$PROJECT --location=$REGION || true

echo "Creating BigQuery Dataset and Table..."
bq mk --location=$REGION -d $PROJECT:test_governance_dataset || true
echo '[{"name": "id", "type": "STRING", "mode": "REQUIRED"}]' > schema.json
bq mk -t $PROJECT:test_governance_dataset.test_table schema.json || true
rm -f schema.json

echo "Creating KMS Key Ring and Key..."
gcloud kms keyrings create $PREFIX-keyring --location=$REGION --project=$PROJECT || true
gcloud kms keys create $PREFIX-key --keyring=$PREFIX-keyring --location=$REGION --purpose=encryption --project=$PROJECT || true

echo "Creating Secret Manager Secret..."
gcloud secrets create $PREFIX-secret --replication-policy="automatic" --project=$PROJECT || true

echo "Creating Pub/Sub Topic and Subscription..."
gcloud pubsub topics create $PREFIX-topic --project=$PROJECT || true
gcloud pubsub subscriptions create $PREFIX-sub --topic=$PREFIX-topic --project=$PROJECT || true

echo "Creating Artifact Registry Repository..."
gcloud artifacts repositories create $PREFIX-repo --repository-format=docker --location=$REGION --project=$PROJECT || true

echo "Creating Cloud Run Service..."
gcloud run deploy $PREFIX-service --image=us-docker.pkg.dev/cloudrun/container/hello --region=$REGION --project=$PROJECT --no-allow-unauthenticated || true

echo "Creating Compute Engine Instance & Disk..."
gcloud compute disks create $PREFIX-disk --size=10GB --zone=$ZONE --project=$PROJECT || true
gcloud compute instances create $PREFIX-instance --machine-type=e2-micro --zone=$ZONE --project=$PROJECT || true

# ------------------------------------------------------------------------------
# HEAVY RESOURCES (Run in background via --async)
# ------------------------------------------------------------------------------
echo "Creating Cloud SQL Instance (Async - Takes ~10 mins)..."
gcloud sql instances create $PREFIX-sql --database-version=POSTGRES_14 --tier=db-f1-micro --region=$REGION --async --project=$PROJECT || true

echo "Creating GKE Cluster (Async - Takes ~15 mins)..."
gcloud container clusters create $PREFIX-gke --region=$REGION --num-nodes=1 --async --project=$PROJECT || true

echo "Creating MemoryStore Redis (Async - Takes ~5 mins)..."
gcloud redis instances create $PREFIX-redis --size=1 --region=$REGION --async --project=$PROJECT || true

echo "All fast resources created. Heavy resources are provisioning in the background!"