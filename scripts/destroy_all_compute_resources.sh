#!/bin/bash
# ==============================================================================
# Script to DESTROY GCP Compute resources created for Label/Tag governance testing
# Project: payments-dev-1
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

# 12. VpnTunnel
echo "Deleting VPN Tunnel..."
gcloud compute vpn-tunnels delete $PREFIX-tunnel \
    --region=$REGION \
    --project=$PROJECT \
    --quiet

# 11. ExternalVpnGateway
echo "Deleting External VPN Gateway..."
gcloud compute external-vpn-gateways delete $PREFIX-ext-vpn \
    --project=$PROJECT \
    --quiet

# 10. VpnGateway (HA VPN)
echo "Deleting HA VPN Gateway..."
gcloud compute vpn-gateways delete $PREFIX-ha-vpn \
    --region=$REGION \
    --project=$PROJECT \
    --quiet

# 9. ForwardingRule
echo "Deleting Forwarding Rule..."
gcloud compute forwarding-rules delete $PREFIX-forwarding-rule \
    --region=$REGION \
    --project=$PROJECT \
    --quiet

# 8. TargetVpnGateway (Classic VPN)
echo "Deleting Target VPN Gateway..."
gcloud compute target-vpn-gateways delete $PREFIX-target-vpn \
    --region=$REGION \
    --project=$PROJECT \
    --quiet

# 7. Router
echo "Deleting Cloud Router..."
gcloud compute routers delete $PREFIX-router \
    --region=$REGION \
    --project=$PROJECT \
    --quiet

# 6. MachineImage
echo "Deleting Machine Image..."
gcloud compute machine-images delete $PREFIX-machine-image \
    --project=$PROJECT \
    --quiet

# 5. Instance
echo "Deleting Instance..."
gcloud compute instances delete $PREFIX-instance \
    --zone=$ZONE \
    --project=$PROJECT \
    --quiet

# 4. Image
echo "Deleting Image..."
gcloud compute images delete $PREFIX-image \
    --project=$PROJECT \
    --quiet

# 3. Snapshot
echo "Deleting Snapshot..."
gcloud compute snapshots delete $PREFIX-snapshot \
    --project=$PROJECT \
    --quiet

# 2. Disk
echo "Deleting Disk..."
gcloud compute disks delete $PREFIX-disk \
    --zone=$ZONE \
    --project=$PROJECT \
    --quiet

# 1. Address
echo "Deleting Address..."
gcloud compute addresses delete $PREFIX-address \
    --region=$REGION \
    --project=$PROJECT \
    --quiet

echo "=============================================================================="
echo "All test resources successfully destroyed in $PROJECT!"
