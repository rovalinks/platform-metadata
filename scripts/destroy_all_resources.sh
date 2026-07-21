#!/bin/bash
# ==============================================================================
# Script to DESTROY all test resources (Compute, Storage, BigQuery, KMS, RM)
# Project: payments-dev-1
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Setting project to $PROJECT..."
gcloud config set project $PROJECT

echo "Deleting VPN Tunnel..."
gcloud compute vpn-tunnels delete $PREFIX-tunnel --region=$REGION --project=$PROJECT --quiet

echo "Deleting External VPN Gateway..."
gcloud compute external-vpn-gateways delete $PREFIX-ext-vpn --project=$PROJECT --quiet

echo "Deleting HA VPN Gateway..."
gcloud compute vpn-gateways delete $PREFIX-ha-vpn --region=$REGION --project=$PROJECT --quiet

echo "Deleting Forwarding Rule..."
gcloud compute forwarding-rules delete $PREFIX-forwarding-rule --project=$PROJECT --quiet

echo "Deleting Target VPN Gateway..."
gcloud compute target-vpn-gateways delete $PREFIX-target-vpn --project=$PROJECT --quiet

echo "Deleting Cloud Router..."
gcloud compute routers delete $PREFIX-router --region=$REGION --project=$PROJECT --quiet

echo "Deleting Machine Image..."
gcloud compute machine-images delete $PREFIX-machine-image --project=$PROJECT --quiet

echo "Deleting Instance..."
gcloud compute instances delete $PREFIX-instance --zone=$ZONE --project=$PROJECT --quiet

echo "Deleting Image..."
gcloud compute images delete $PREFIX-image --project=$PROJECT --quiet

echo "Deleting Snapshot..."
gcloud compute snapshots delete $PREFIX-snapshot --project=$PROJECT --quiet

echo "Deleting Disk..."
gcloud compute disks delete $PREFIX-disk --zone=$ZONE --project=$PROJECT --quiet

echo "Deleting Address..."
gcloud compute addresses delete $PREFIX-address --region=$REGION --project=$PROJECT --quiet

echo "Deleting BigQuery Dataset and contents..."
bq rm -r -f -d $PROJECT:test_governance_dataset

echo "Deleting Storage Bucket..."
gcloud storage rm -r gs://payments-dev-1-governance-test-bucket

TAG_KEY_ID=$(gcloud resource-manager tags keys list --parent="projects/$(gcloud projects describe $PROJECT --format="value(projectNumber)")" --filter="shortName=$PREFIX-tagkey" --format="value(name)" 2>/dev/null)
if [ ! -z "$TAG_KEY_ID" ]; then
  echo "Deleting Resource Manager Tag Key: $TAG_KEY_ID"
  gcloud resource-manager tags keys delete "$TAG_KEY_ID" --quiet
fi

echo "=============================================================================="
echo "All test resources successfully destroyed in $PROJECT!"