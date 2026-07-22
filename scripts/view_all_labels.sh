#!/bin/bash
# ==============================================================================
# Script to view labels/metadata for all 32 governed resources
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Listing labels for all test resources in $PROJECT..."
printf "%-35s | %-25s | \n" "RESOURCE TYPE" "RESOURCE NAME"
echo "------------------------------------------------------------------------"

printf "%-35s | %-25s | " "storage-bucket" "$PROJECT-$PREFIX-bucket"
gcloud storage buckets describe gs://$PROJECT-$PREFIX-bucket --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "bigquery-dataset" "${PREFIX}_dataset"
bq show --format=prettyjson $PROJECT:${PREFIX}_dataset | grep -A 5 "labels" || echo "N/A"

printf "%-35s | %-25s | " "bigquery-table" "${PREFIX}_table"
bq show --format=prettyjson $PROJECT:${PREFIX}_dataset.${PREFIX}_table | grep -A 5 "labels" || echo "N/A"

printf "%-35s | %-25s | " "kms-key" "$PREFIX-key"
gcloud kms keys describe $PREFIX-key --keyring=$PREFIX-keyring --location=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "secret-manager" "$PREFIX-secret"
gcloud secrets describe $PREFIX-secret --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "pubsub-topic" "$PREFIX-topic"
gcloud pubsub topics describe $PREFIX-topic --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "pubsub-subscription" "$PREFIX-sub"
gcloud pubsub subscriptions describe projects/$PROJECT/subscriptions/$PREFIX-sub --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "artifact-registry" "$PREFIX-repo"
gcloud artifacts repositories describe $PREFIX-repo --location=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "cloud-run" "$PREFIX-service"
gcloud run services describe $PREFIX-service --region=$REGION --project=$PROJECT --format="value(metadata.labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "compute-instance" "$PREFIX-instance"
gcloud compute instances describe $PREFIX-instance --zone=$ZONE --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "compute-disk" "$PREFIX-disk"
gcloud compute disks describe $PREFIX-disk --zone=$ZONE --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "compute-address" "$PREFIX-address"
gcloud compute addresses describe $PREFIX-address --region=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "compute-snapshot" "$PREFIX-snapshot"
gcloud compute snapshots describe $PREFIX-snapshot --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "compute-image" "$PREFIX-image"
gcloud compute images describe $PREFIX-image --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "cloud-dns" "$PREFIX-zone"
gcloud dns managed-zones describe $PREFIX-zone --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "dataform-repository" "$PREFIX-dataform"
gcloud dataform repositories describe $PREFIX-dataform --location=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "dataplex-entrygroup" "$PREFIX-entrygroup"
gcloud dataplex entry-groups describe $PREFIX-entrygroup --location=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "N/A"

printf "%-35s | %-25s | " "cloud-sql (If Ready)" "$PREFIX-sql"
gcloud sql instances describe $PREFIX-sql --project=$PROJECT --format="value(settings.userLabels)" 2>/dev/null || echo "Not Ready"

printf "%-35s | %-25s | " "gke-cluster (If Ready)" "$PREFIX-gke"
gcloud container clusters describe $PREFIX-gke --region=$REGION --project=$PROJECT --format="value(resourceLabels)" 2>/dev/null || echo "Not Ready"

printf "%-35s | %-25s | " "redis (If Ready)" "$PREFIX-redis"
gcloud redis instances describe $PREFIX-redis --region=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "Not Ready"

printf "%-35s | %-25s | " "alloydb (If Ready)" "$PREFIX-alloy-cluster"
gcloud alloydb clusters describe $PREFIX-alloy-cluster --region=$REGION --project=$PROJECT --format="value(labels)" 2>/dev/null || echo "Not Ready"