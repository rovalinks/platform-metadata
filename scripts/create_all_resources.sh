#!/bin/bash
# ==============================================================================
# Script to provision GCP Compute, Storage, BigQuery, KMS, and Resource Manager
# Project: payments-dev-1
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
NETWORK="default"
PREFIX="test-gov"

echo "Setting project to $PROJECT..."
gcloud config set project $PROJECT

echo "Ensuring required APIs are enabled..."
gcloud services enable compute.googleapis.com bigquery.googleapis.com storage.googleapis.com cloudkms.googleapis.com cloudresourcemanager.googleapis.com

# ------------------------------------------------------------------------------
# 0. Storage, BigQuery, KMS, & Resource Manager Test Resources
# ------------------------------------------------------------------------------
echo "Creating Storage Bucket..."
gcloud storage buckets create gs://payments-dev-1-governance-test-bucket --project=$PROJECT --location=$REGION

echo "Creating BigQuery Dataset..."
bq mk --location=$REGION -d $PROJECT:test_governance_dataset

echo "Creating BigQuery Table schema..."
echo '[{"name": "id", "type": "STRING", "mode": "REQUIRED"}]' > schema.json

echo "Creating BigQuery Table..."
bq mk -t $PROJECT:test_governance_dataset.test_table schema.json
rm -f schema.json

echo "Creating KMS Key Ring..."
gcloud kms keyrings create $PREFIX-keyring --location=$REGION --project=$PROJECT

echo "Creating KMS Crypto Key..."
gcloud kms keys create $PREFIX-key --keyring=$PREFIX-keyring --location=$REGION --purpose=encryption --project=$PROJECT

echo "Creating Resource Manager Tag Key..."
gcloud resource-manager tags keys create $PREFIX-tagkey --parent="projects/$(gcloud projects describe $PROJECT --format="value(projectNumber)")" --purpose=GCE_FIREWALL --purpose-data=network=$PROJECT/global/networks/$NETWORK || echo "Tag key might already exist"

# ------------------------------------------------------------------------------
# Compute Engine Resources
# ------------------------------------------------------------------------------
echo "Creating Address..."
gcloud compute addresses create $PREFIX-address \
    --region=$REGION \
    --project=$PROJECT

echo "Creating Disk..."
gcloud compute disks create $PREFIX-disk \
    --size=10GB \
    --zone=$ZONE \
    --project=$PROJECT

echo "Creating Snapshot..."
gcloud compute snapshots create $PREFIX-snapshot \
    --source-disk=$PREFIX-disk \
    --source-disk-zone=$ZONE \
    --project=$PROJECT

echo "Creating Image..."
gcloud compute images create $PREFIX-image \
    --source-disk=$PREFIX-disk \
    --source-disk-zone=$ZONE \
    --project=$PROJECT

echo "Creating Instance..."
gcloud compute instances create $PREFIX-instance \
    --machine-type=e2-micro \
    --zone=$ZONE \
    --project=$PROJECT

echo "Creating Machine Image..."
gcloud compute machine-images create $PREFIX-machine-image \
    --source-instance=$PREFIX-instance \
    --source-instance-zone=$ZONE \
    --project=$PROJECT

echo "Creating Cloud Router..."
gcloud compute routers create $PREFIX-router \
    --region=$REGION \
    --network=$NETWORK \
    --asn=65001 \
    --project=$PROJECT

echo "Creating Target VPN Gateway (Classic)..."
gcloud compute target-vpn-gateways create $PREFIX-target-vpn \
    --region=$REGION \
    --network=$NETWORK \
    --project=$PROJECT

echo "Creating Forwarding Rule..."
gcloud compute forwarding-rules create $PREFIX-forwarding-rule \
    --region=$REGION \
    --target-vpn-gateway=$PREFIX-target-vpn \
    --ip-protocol=ESP \
    --project=$PROJECT

echo "Creating HA VPN Gateway..."
gcloud compute vpn-gateways create $PREFIX-ha-vpn \
    --network=$NETWORK \
    --region=$REGION \
    --project=$PROJECT

echo "Creating External VPN Gateway..."
gcloud compute external-vpn-gateways create $PREFIX-ext-vpn \
    --interfaces 0=8.8.8.8 \
    --project=$PROJECT

echo "Creating VPN Tunnel..."
gcloud compute vpn-tunnels create $PREFIX-tunnel \
    --region=$REGION \
    --peer-external-gateway=$PREFIX-ext-vpn \
    --peer-external-gateway-interface=0 \
    --router=$PREFIX-router \
    --vpn-gateway=$PREFIX-ha-vpn \
    --interface=0 \
    --project=$PROJECT

echo "=============================================================================="
echo "All test resources (Compute, Storage, BQ, KMS, RM) provisioned successfully in $PROJECT!"