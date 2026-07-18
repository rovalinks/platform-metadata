#!/bin/bash

# Configuration
TEST_PROJECT="payments-dev-1"
ZONE="europe-west2-a"
REGION="europe-west2"

echo "🚀 Firing real-time creation events in ${TEST_PROJECT}..."

# 1. Create a dummy Instance
echo "Creating Instance..."
gcloud compute instances create test-gov-instance \
    --project=${TEST_PROJECT} --zone=${ZONE} --machine-type=e2-micro

# 2. Create a dummy Disk
echo "Creating Disk..."
gcloud compute disks create test-gov-disk \
    --project=${TEST_PROJECT} --zone=${ZONE} --size=10GB

# 3. Create a dummy IP Address
echo "Creating Address..."
gcloud compute addresses create test-gov-address \
    --project=${TEST_PROJECT} --region=${REGION}

echo "✅ Test resources created!"
echo "Your Log Router is now pushing these to Pub/Sub -> Cloud Run.":wq

