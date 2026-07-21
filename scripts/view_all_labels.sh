#!/bin/bash
# ==============================================================================
# Script to view labels/metadata for test resources in payments-dev-1
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Listing labels for all test resources in $PROJECT..."
echo "----------------------------------------------------"

show_labels() {
    local resource_type=$1
    local resource_name=$2
    local flags=$3
    
    printf "%-25s | %-20s | " "$resource_type" "$resource_name"
    gcloud compute $resource_type describe $resource_name $flags --project=$PROJECT --format="value(labels)"
}

printf "%-25s | %-20s | " "storage-bucket" "governance-test-bucket"
gcloud storage buckets describe gs://payments-dev-1-governance-test-bucket --format="value(labels)"

printf "%-25s | %-20s | " "bigquery-dataset" "test_governance_dataset"
bq show --format=prettyjson $PROJECT:test_governance_dataset | grep -A 5 "labels" || echo "No labels found"

printf "%-25s | %-20s | " "kms-key" "$PREFIX-key"
gcloud kms keys describe $PREFIX-key --keyring=$PREFIX-keyring --location=$REGION --project=$PROJECT --format="value(labels)"

printf "%-25s | %-20s | " "project-metaconfig" "$PROJECT"
gcloud projects describe $PROJECT --format="json" | grep -A 5 "labels" || echo "No labels found"

show_labels "addresses" "$PREFIX-address" "--region=$REGION"
show_labels "disks" "$PREFIX-disk" "--zone=$ZONE"
show_labels "snapshots" "$PREFIX-snapshot" ""
show_labels "images" "$PREFIX-image" ""
show_labels "instances" "$PREFIX-instance" "--zone=$ZONE"
show_labels "machine-images" "$PREFIX-machine-image" ""
show_labels "routers" "$PREFIX-router" "--region=$REGION"
show_labels "target-vpn-gateways" "$PREFIX-target-vpn" "--region=$REGION"
show_labels "forwarding-rules" "$PREFIX-forwarding-rule" "--region=$REGION"
show_labels "vpn-gateways" "$PREFIX-ha-vpn" "--region=$REGION"
show_labels "external-vpn-gateways" "$PREFIX-ext-vpn" ""
show_labels "vpn-tunnels" "$PREFIX-tunnel" "--region=$REGION"

echo "----------------------------------------------------"
echo "Done."