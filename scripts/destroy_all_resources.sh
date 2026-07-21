#!/bin/bash
# ==============================================================================
# Script to DESTROY all test resources
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Setting project to $PROJECT..."
gcloud config set project $PROJECT

echo "Deleting Cloud Run Service..."
gcloud run services delete $PREFIX-service --region=$REGION --project=$PROJECT --quiet

echo "Deleting Artifact Registry Repository..."
gcloud artifacts repositories delete $PREFIX-repo --location=$REGION --project=$PROJECT --quiet

echo "Deleting Pub/Sub Subscription and Topic..."
gcloud pubsub subscriptions delete $PREFIX-sub --project=$PROJECT --quiet
gcloud pubsub topics delete $PREFIX-topic --project=$PROJECT --quiet

echo "Deleting Secret Manager Secret..."
gcloud secrets delete $PREFIX-secret --project=$PROJECT --quiet

echo "Deleting Compute Engine Instance and Disk..."
gcloud compute instances delete $PREFIX-instance --zone=$ZONE --project=$PROJECT --quiet
gcloud compute disks delete $PREFIX-disk --zone=$ZONE --project=$PROJECT --quiet

echo "Deleting BigQuery Dataset and contents..."
bq rm -r -f -d $PROJECT:test_governance_dataset

echo "Deleting Storage Bucket..."
gcloud storage rm -r gs://payments-dev-1-governance-test-bucket

echo "Deleting Heavy Resources (Running in background via --async)..."
gcloud sql instances delete $PREFIX-sql --project=$PROJECT --async --quiet || true
gcloud container clusters delete $PREFIX-gke --region=$REGION --project=$PROJECT --async --quiet || true
gcloud redis instances delete $PREFIX-redis --region=$REGION --project=$PROJECT --async --quiet || true

echo "Cleanup initiated! Heavy resources will finish deleting in the background."