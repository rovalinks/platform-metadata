import re
from google.cloud import compute_v1
from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent

class ComputeClassifier(ResourceClassifier):
    """
    Comprehensive Classifier for Google Cloud Compute Engine.
    Handles creation, attachment, and modification lifecycle events.
    """

    SERVICE = "compute.googleapis.com"

    # Full registry of supported Compute Engine resources
    SERVICE_REGISTRY = {
        # --- Compute ---
        ("instances", "zones"): {"asset_type": "compute.googleapis.com/Instance", "client_attr": "instances"},
        ("disks", "zones"): {"asset_type": "compute.googleapis.com/Disk", "client_attr": "disks"},
        ("disks", "regions"): {"asset_type": "compute.googleapis.com/Disk", "client_attr": "region_disks"},
        ("instanceGroups", "zones"): {"asset_type": "compute.googleapis.com/InstanceGroup", "client_attr": "instance_groups"},
        
        # --- Networking ---
        ("subnetworks", "regions"): {"asset_type": "compute.googleapis.com/Subnetwork", "client_attr": "subnetworks"},
        ("networks", "global"): {"asset_type": "compute.googleapis.com/Network", "client_attr": "networks"},
        ("firewalls", "global"): {"asset_type": "compute.googleapis.com/Firewall", "client_attr": "firewalls"},
        ("addresses", "regions"): {"asset_type": "compute.googleapis.com/Address", "client_attr": "addresses"},
        ("addresses", "global"): {"asset_type": "compute.googleapis.com/Address", "client_attr": "global_addresses"},
        
        # --- Load Balancing & Security ---
        ("forwardingRules", "global"): {"asset_type": "compute.googleapis.com/ForwardingRule", "client_attr": "global_forwarding_rules"},
        ("forwardingRules", "regions"): {"asset_type": "compute.googleapis.com/ForwardingRule", "client_attr": "forwarding_rules"},
        ("backendServices", "global"): {"asset_type": "compute.googleapis.com/BackendService", "client_attr": "backend_services"},
        ("urlMaps", "global"): {"asset_type": "compute.googleapis.com/UrlMap", "client_attr": "url_maps"},
        ("targetHttpsProxies", "global"): {"asset_type": "compute.googleapis.com/TargetHttpsProxy", "client_attr": "target_https_proxies"},
        ("targetHttpProxies", "global"): {"asset_type": "compute.googleapis.com/TargetHttpProxy", "client_attr": "target_http_proxies"},
        ("sslCertificates", "global"): {"asset_type": "compute.googleapis.com/SslCertificate", "client_attr": "ssl_certificates"},
        
        # --- Images & Storage ---
        ("images", "global"): {"asset_type": "compute.googleapis.com/Image", "client_attr": "images"},
        ("snapshots", "global"): {"asset_type": "compute.googleapis.com/Snapshot", "client_attr": "snapshots"},
        ("machineImages", "global"): {"asset_type": "compute.googleapis.com/MachineImage", "client_attr": "machine_images"},
        
        # --- VPN ---
        ("vpnTunnels", "regions"): {"asset_type": "compute.googleapis.com/VpnTunnel", "client_attr": "vpn_tunnels"},
        ("vpnGateways", "regions"): {"asset_type": "compute.googleapis.com/VpnGateway", "client_attr": "vpn_gateways"},
    }

    def _resolve_key(self, event: AuditLogEvent):
        # 1. Normalize method name (Strip versions)
        method = self.normalize_method(event.method_name).replace("compute.", "").replace("beta.", "").replace("v1.", "")
        
        # 2. Determine Scope
        scope = "global"
        if "/zones/" in event.resource_name:
            scope = "zones"
        elif "/regions/" in event.resource_name:
            scope = "regions"
            
        # 3. Check for Operations
        # A. Creation/Deletion (e.g., instances.insert, firewalls.insert, disks.delete)
        for (collection, s), metadata in self.SERVICE_REGISTRY.items():
            if s == scope and (method == f"{collection}.insert" or method == f"{collection}.delete"):
                return (collection, s)
        
        # B. Modifications/Attachments (Specific to VM lifecycle)
        if "instances" in event.resource_name:
            if any(op in method for op in [
                "attachDisk", "detachDisk", "addAccessConfig", 
                "deleteAccessConfig", "stop", "start", "reset"
            ]):
                return ("instances", "zones")
        
        return None

    def supports(self, event: AuditLogEvent) -> bool:
        return self._resolve_key(event) is not None

    def classify(self, event: AuditLogEvent) -> ResourceEvent:
        key = self._resolve_key(event)
        metadata = self.SERVICE_REGISTRY[key]
        
        return ResourceEvent(
            project_id=event.project_id,
            asset_type=metadata["asset_type"],
            resource_name=event.resource_name,
            service_name=self.SERVICE,
            method_name=event.method_name,
            location=event.location,
        )
