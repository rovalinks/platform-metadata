#!/bin/bash
# ==============================================================================
# Script to DESTROY all test resources safely (Matching full resource maps)
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Setting project to $PROJECT..."
gcloud config set project $PROJECT

echo "Deleting Cloud Run Service..."
gcloud run services delete $PREFIX-service --region=$REGION --project=$PROJECT --quiet || true

echo "Deleting Artifact Registry Repository..."
gcloud artifacts repositories delete $PREFIX-repo --location=$REGION --project=$PROJECT --quiet || true

echo "Deleting Pub/Sub Subscription and Topic..."
gcloud pubsub subscriptions delete $PREFIX-sub --project=$PROJECT --quiet || true
gcloud pubsub topics delete $PREFIX-topic --project=$PROJECT --quiet || true

echo "Deleting Secret Manager Secret..."
gcloud secrets delete $PREFIX-secret --project=$PROJECT --quiet || true

echo "Deleting Compute Engine Resources & Networking..."
gcloud compute instances delete $PREFIX-instance --zone=$ZONE --project=$PROJECT --quiet || true
gcloud compute disks delete $PREFIX-disk --zone=$ZONE --project=$PROJECT --quiet || true
gcloud compute addresses delete $PREFIX-address --region=$REGION --project=$PROJECT --quiet || true
gcloud compute snapshots delete $PREFIX-snapshot --project=$PROJECT --quiet || true
gcloud compute images delete $PREFIX-image --project=$PROJECT --quiet || true

gcloud compute firewalls delete $PREFIX-fw --project=$PROJECT --quiet || true
gcloud compute routers nats delete $PREFIX-nat --router=$PREFIX-router --region=$REGION --project=$PROJECT --quiet || true
gcloud compute routers delete $PREFIX-router --region=$REGION --project=$PROJECT --quiet || true
gcloud compute networks subnets delete $PREFIX-subnetwork --region=$REGION --project=$PROJECT --quiet || true
gcloud compute networks delete $PREFIX-network --project=$PROJECT --quiet || true

echo "Deleting Cloud DNS..."
gcloud dns managed-zones delete $PREFIX-zone --project=$PROJECT --quiet || true

echo "Deleting Dataform Repository & Dataplex EntryGroup..."
gcloud dataform repositories delete $PREFIX-dataform --location=$REGION --project=$PROJECT --quiet || true
gcloud dataplex entry-groups delete $PREFIX-entrygroup --location=$REGION --project=$PROJECT || true

echo "Deleting BigQuery Dataset and contents..."
bq rm -r -f -d $PROJECT:${PREFIX}_dataset || true

echo "Deleting Storage Bucket..."
gcloud storage rm -r gs://$PROJECT-$PREFIX-bucket || true

# ------------------------------------------------------------------------------
# HEAVY RESOURCES (Async deletes)
# ------------------------------------------------------------------------------
echo "Deleting Heavy Resources (Running in background via --async)..."
gcloud sql instances delete $PREFIX-sql --project=$PROJECT --async --quiet || true
gcloud container clusters delete $PREFIX-gke --region=$REGION --project=$PROJECT --async --quiet || true
gcloud redis instances delete $PREFIX-redis --region=$REGION --project=$PROJECT --async --quiet || true
gcloud alloydb instances delete $PREFIX-alloy-instance --cluster=$PREFIX-alloy-cluster --region=$REGION --project=$PROJECT --async --quiet || true
gcloud alloydb clusters delete $PREFIX-alloy-cluster --region=$REGION --project=$PROJECT --async --quiet || true

echo "Cleanup initiated! Heavy resources will finish deleting in the background."