#!/bin/bash
# ==============================================================================
# Script to remove 'costcenter' label from ALL test-gov resources
# ==============================================================================

PROJECT="payments-dev-1"
REGION="europe-west2"
ZONE="europe-west2-a"
PREFIX="test-gov"
LABEL_TO_REMOVE="costcenter"

echo "Attempting to remove '$LABEL_TO_REMOVE' from all resources..."

remove_label() {
    local type=$1
    local name=$2
    local flags=$3

    printf "Processing %-20s / %-25s : " "$type" "$name"

    # 1. Try standard remove-labels or update --remove-labels (Simple path)
    if gcloud compute $type remove-labels $name $flags --labels=$LABEL_TO_REMOVE --project=$PROJECT --quiet >/dev/null 2>&1 || \
       gcloud compute $type update $name $flags --remove-labels=$LABEL_TO_REMOVE --project=$PROJECT --quiet >/dev/null 2>&1; then
        echo "SUCCESS (Auto)"
    else
        # 2. Fallback: Manual Get/Set path for VPN/Gateways
        local json=$(gcloud compute $type describe $name $flags --project=$PROJECT --format="json")
        local fingerprint=$(echo "$json" | jq -r '.labelFingerprint')
        local current_labels=$(echo "$json" | jq -r ".labels | del(.$LABEL_TO_REMOVE)")

        if [ "$current_labels" == "{}" ] || [ "$current_labels" == "null" ]; then
            echo "SKIPPED (No labels found)"
        else
            if gcloud compute $type set-labels $name $flags --labels="$current_labels" --label-fingerprint="$fingerprint" --project=$PROJECT --quiet >/dev/null 2>&1; then
                echo "SUCCESS (Manual)"
            else
                echo "FAILED (Resource may be immutable or locked)"
            fi
        fi
    fi
}

# --- Resource List ---
remove_label "addresses" "$PREFIX-address" "--region=$REGION"
remove_label "disks" "$PREFIX-disk" "--zone=$ZONE"
remove_label "snapshots" "$PREFIX-snapshot" ""
remove_label "images" "$PREFIX-image" ""
remove_label "instances" "$PREFIX-instance" "--zone=$ZONE"
# Machine Images are immutable: they cannot be modified after creation.
echo "Processing machine-images/test-gov-machine-image : SKIPPED (Immutable)"
remove_label "target-vpn-gateways" "$PREFIX-target-vpn" "--region=$REGION"
remove_label "forwarding-rules" "$PREFIX-forwarding-rule" "--region=$REGION"
remove_label "vpn-gateways" "$PREFIX-ha-vpn" "--region=$REGION"
remove_label "external-vpn-gateways" "$PREFIX-ext-vpn" ""
remove_label "vpn-tunnels" "$PREFIX-tunnel" "--region=$REGION"
remove_label "routers" "$PREFIX-router" "--region=$REGION"

echo "----------------------------------------------------"
echo "Done."