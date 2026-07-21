#!/bin/bash
# ==============================================================================
# Script to view labels/metadata for all test resources
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Listing labels for all test resources in $PROJECT..."
echo "----------------------------------------------------"

printf "%-30s | %-25s | \n" "RESOURCE TYPE" "RESOURCE NAME"
echo "------------------------------------------------------------------------"

printf "%-30s | %-25s | " "storage-bucket" "governance-test-bucket"
gcloud storage buckets describe gs://payments-dev-1-governance-test-bucket --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "bigquery-dataset" "test_governance_dataset"
bq show --format=prettyjson $PROJECT:test_governance_dataset | grep -A 5 "labels" || echo "No labels found"

printf "%-30s | %-25s | " "kms-key" "$PREFIX-key"
gcloud kms keys describe $PREFIX-key --keyring=$PREFIX-keyring --location=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "secret-manager" "$PREFIX-secret"
gcloud secrets describe $PREFIX-secret --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "pubsub-topic" "$PREFIX-topic"
gcloud pubsub topics describe projects/$PROJECT/topics/$PREFIX-topic --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "pubsub-subscription" "$PREFIX-sub"
gcloud pubsub subscriptions describe projects/$PROJECT/subscriptions/$PREFIX-sub --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "artifact-registry" "$PREFIX-repo"
gcloud artifacts repositories describe $PREFIX-repo --location=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "cloud-run" "$PREFIX-service"
gcloud run services describe $PREFIX-service --region=$REGION --project=$PROJECT --format="value(metadata.labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "compute-instance" "$PREFIX-instance"
gcloud compute instances describe $PREFIX-instance --zone=$ZONE --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-30s | %-25s | " "cloud-sql (If Ready)" "$PREFIX-sql"
gcloud sql instances describe $PREFIX-sql --project=$PROJECT --format="value(settings.userLabels)" 2>/dev/null || echo "Not Ready"

printf "%-30s | %-25s | " "redis (If Ready)" "$PREFIX-redis"
gcloud redis instances describe $PREFIX-redis --region=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "Not Ready"

printf "%-30s | %-25s | " "gke-cluster (If Ready)" "$PREFIX-gke"
gcloud container clusters describe $PREFIX-gke --region=$REGION --project=$PROJECT --format="value(resourceLabels)" 2>/dev/null || echo "Not Ready"

echo "------------------------------------------------------------------------"