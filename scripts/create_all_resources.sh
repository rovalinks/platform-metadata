#!/bin/bash
# ==============================================================================
# Script to provision GCP Test Resources across ALL 32 governed services
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Setting project to $PROJECT..."
gcloud config set project $PROJECT

echo "Ensuring required APIs are enabled (This may take a moment)..."
gcloud services enable compute.googleapis.com bigquery.googleapis.com storage.googleapis.com cloudkms.googleapis.com cloudresourcemanager.googleapis.com secretmanager.googleapis.com pubsub.googleapis.com artifactregistry.googleapis.com run.googleapis.com sqladmin.googleapis.com container.googleapis.com redis.googleapis.com aiplatform.googleapis.com dataplex.googleapis.com dataform.googleapis.com dns.googleapis.com monitoring.googleapis.com alloydb.googleapis.com appengine.googleapis.com cloudfunctions.googleapis.com --async

# ------------------------------------------------------------------------------
# FAST RESOURCES
# ------------------------------------------------------------------------------
echo "Creating Cloud Storage Bucket..."
gcloud storage buckets create gs://$PROJECT-$PREFIX-bucket --project=$PROJECT --location=$REGION || true

echo "Creating BigQuery Dataset & Table..."
bq mk --location=$REGION -d $PROJECT:${PREFIX}_dataset || true
echo '[{"name": "id", "type": "STRING", "mode": "REQUIRED"}]' > schema.json
bq mk -t $PROJECT:${PREFIX}_dataset.${PREFIX}_table schema.json || true
rm schema.json

echo "Creating Secret Manager Secret..."
gcloud secrets create $PREFIX-secret --replication-policy="automatic" --project=$PROJECT || true

echo "Creating Pub/Sub Topic and Subscription..."
gcloud pubsub topics create $PREFIX-topic --project=$PROJECT || true
gcloud pubsub subscriptions create $PREFIX-sub --topic=$PREFIX-topic --project=$PROJECT || true

echo "Creating Artifact Registry Repository..."
gcloud artifacts repositories create $PREFIX-repo --repository-format=docker --location=$REGION --project=$PROJECT || true

echo "Creating Cloud Run Service..."
gcloud run deploy $PREFIX-service --image=us-docker.pkg.dev/cloudrun/container/hello --region=$REGION --project=$PROJECT --no-allow-unauthenticated || true

echo "Creating KMS KeyRing and CryptoKey..."
gcloud kms keyrings create $PREFIX-keyring --location=$REGION --project=$PROJECT || true
gcloud kms keys create $PREFIX-key --keyring=$PREFIX-keyring --location=$REGION --purpose="encryption" --project=$PROJECT || true

echo "Creating Compute Engine Disk, Instance, Address, Snapshot, and Image..."
gcloud compute disks create $PREFIX-disk --size=10GB --zone=$ZONE --project=$PROJECT || true
gcloud compute instances create $PREFIX-instance --machine-type=e2-micro --zone=$ZONE --project=$PROJECT || true
gcloud compute addresses create $PREFIX-address --region=$REGION --project=$PROJECT || true
gcloud compute snapshots create $PREFIX-snapshot --source-disk=$PREFIX-disk --source-disk-zone=$ZONE --project=$PROJECT || true
gcloud compute images create $PREFIX-image --source-disk=$PREFIX-disk --source-disk-zone=$ZONE --project=$PROJECT || true

echo "Creating Cloud DNS Managed Zone..."
gcloud dns managed-zones create $PREFIX-zone --dns-name="testgov.internal." --description="Gov Test" --visibility="private" --project=$PROJECT || true

echo "Creating Dataform Repository..."
gcloud dataform repositories create $PREFIX-dataform --location=$REGION --project=$PROJECT || true

echo "Creating Vertex AI Dataset..."
gcloud ai datasets create --display-name=$PREFIX-vertex-ds --region=$REGION --project=$PROJECT || true

echo "Creating Dataplex EntryGroup..."
gcloud dataplex entry-groups create $PREFIX-entrygroup --location=$REGION --project=$PROJECT || true

echo "Creating Monitoring Alert Policy..."
cat <<EOF > alert.json
{"displayName": "$PREFIX-alert","combiner": "OR","conditions": [{"displayName": "Test","conditionAbsent": {"duration": "300s"}}]}
EOF
gcloud alpha monitoring policies create --policy-from-file=alert.json --project=$PROJECT || true
rm alert.json

echo "Creating App Engine Application..."
gcloud app create --region=$REGION --project=$PROJECT || true

# ------------------------------------------------------------------------------
# HEAVY RESOURCES (Run in background via --async)
# ------------------------------------------------------------------------------
echo "Creating Cloud SQL Instance (Async)..."
gcloud sql instances create $PREFIX-sql --database-version=POSTGRES_14 --tier=db-f1-micro --region=$REGION --async --project=$PROJECT || true

echo "Creating GKE Cluster (Async)..."
gcloud container clusters create $PREFIX-gke --region=$REGION --num-nodes=1 --async --project=$PROJECT || true

echo "Creating MemoryStore Redis (Async)..."
gcloud redis instances create $PREFIX-redis --size=1 --region=$REGION --async --project=$PROJECT || true

echo "Creating AlloyDB Cluster (Async)..."
gcloud alloydb clusters create $PREFIX-alloy-cluster --region=$REGION --password="SuperSecretPassword123" --project=$PROJECT --async || true

echo "All creation commands executed. Heavy resources are provisioning in the background!"