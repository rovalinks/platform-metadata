#!/bin/bash
# ==============================================================================
# Script to view labels for test-gov resources in payments-dev-1
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"

echo "Listing labels for all test resources in $PROJECT..."
echo "----------------------------------------------------"

# Function to display labels for a resource
show_labels() {
    local resource_type=$1
    local resource_name=$2
    local flags=$3
    
    printf "%-25s | %-20s | " "$resource_type" "$resource_name"
    gcloud compute $resource_type describe $resource_name $flags --project=$PROJECT --format="value(labels)"
}

# 1. Address
show_labels "addresses" "$PREFIX-address" "--region=$REGION"

# 2. Disk
show_labels "disks" "$PREFIX-disk" "--zone=$ZONE"

# 3. Snapshot
show_labels "snapshots" "$PREFIX-snapshot" ""

# 4. Image
show_labels "images" "$PREFIX-image" ""

# 5. Instance
show_labels "instances" "$PREFIX-instance" "--zone=$ZONE"

# 6. Machine Image
show_labels "machine-images" "$PREFIX-machine-image" ""

# 7. Router
show_labels "routers" "$PREFIX-router" "--region=$REGION"

# 8. Target VPN Gateway
show_labels "target-vpn-gateways" "$PREFIX-target-vpn" "--region=$REGION"

# 9. Forwarding Rule
show_labels "forwarding-rules" "$PREFIX-forwarding-rule" "--region=$REGION"

# 10. HA VPN Gateway
show_labels "vpn-gateways" "$PREFIX-ha-vpn" "--region=$REGION"

# 11. External VPN Gateway
show_labels "external-vpn-gateways" "$PREFIX-ext-vpn" ""

# 12. VPN Tunnel
show_labels "vpn-tunnels" "$PREFIX-tunnel" "--region=$REGION"

echo "----------------------------------------------------"
echo "Done."
