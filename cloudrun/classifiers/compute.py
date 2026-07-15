import re
from google.cloud import compute_v1
from classifiers.base import ResourceClassifier
from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent

class ComputeClassifier(ResourceClassifier):
    """Classifies all Compute Engine resources using a central registry."""

    SERVICE = "compute.googleapis.com"

    SERVICE_REGISTRY = {
        ("instances", "zones"): {"asset_type": "compute.googleapis.com/Instance", "client_attr": "instances", "get_arg": "instance", "set_labels_request_cls": compute_v1.InstancesSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "instances_set_labels_request_resource"},
        ("disks", "zones"): {"asset_type": "compute.googleapis.com/Disk", "client_attr": "disks", "get_arg": "disk", "set_labels_request_cls": compute_v1.ZoneSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "zone_set_labels_request_resource"},
        ("networkEndpointGroups", "zones"): {"asset_type": "compute.googleapis.com/NetworkEndpointGroup", "client_attr": "network_endpoint_groups", "get_arg": "network_endpoint_group", "set_labels_request_cls": compute_v1.ZoneSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "zone_set_labels_request_resource"},
        ("instanceGroups", "zones"): {"asset_type": "compute.googleapis.com/InstanceGroup", "client_attr": "instance_groups", "get_arg": "instance_group", "set_labels_request_cls": compute_v1.ZoneSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "zone_set_labels_request_resource"},
        ("disks", "regions"): {"asset_type": "compute.googleapis.com/Disk", "client_attr": "region_disks", "get_arg": "disk", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("subnetworks", "regions"): {"asset_type": "compute.googleapis.com/Subnetwork", "client_attr": "subnetworks", "get_arg": "subnetwork", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("healthChecks", "regions"): {"asset_type": "compute.googleapis.com/HealthCheck", "client_attr": "region_health_checks", "get_arg": "health_check", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("backendServices", "regions"): {"asset_type": "compute.googleapis.com/BackendService", "client_attr": "region_backend_services", "get_arg": "backend_service", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("forwardingRules", "regions"): {"asset_type": "compute.googleapis.com/ForwardingRule", "client_attr": "forwarding_rules", "get_arg": "forwarding_rule", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("addresses", "regions"): {"asset_type": "compute.googleapis.com/Address", "client_attr": "addresses", "get_arg": "address", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("sslCertificates", "regions"): {"asset_type": "compute.googleapis.com/SslCertificate", "client_attr": "region_ssl_certificates", "get_arg": "ssl_certificate", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("targetHttpsProxies", "regions"): {"asset_type": "compute.googleapis.com/TargetHttpsProxy", "client_attr": "region_target_https_proxies", "get_arg": "target_https_proxy", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("urlMaps", "regions"): {"asset_type": "compute.googleapis.com/UrlMap", "client_attr": "region_url_maps", "get_arg": "url_map", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("targetHttpProxies", "regions"): {"asset_type": "compute.googleapis.com/TargetHttpProxy", "client_attr": "region_target_http_proxies", "get_arg": "target_http_proxy", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("instanceGroups", "regions"): {"asset_type": "compute.googleapis.com/InstanceGroup", "client_attr": "region_instance_groups", "get_arg": "instance_group", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("vpnTunnels", "regions"): {"asset_type": "compute.googleapis.com/VpnTunnel", "client_attr": "vpn_tunnels", "get_arg": "vpn_tunnel", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("vpnGateways", "regions"): {"asset_type": "compute.googleapis.com/VpnGateway", "client_attr": "vpn_gateways", "get_arg": "vpn_gateway", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("healthChecks", "global"): {"asset_type": "compute.googleapis.com/HealthCheck", "client_attr": "health_checks", "get_arg": "health_check", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("backendServices", "global"): {"asset_type": "compute.googleapis.com/BackendService", "client_attr": "backend_services", "get_arg": "backend_service", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("forwardingRules", "global"): {"asset_type": "compute.googleapis.com/ForwardingRule", "client_attr": "global_forwarding_rules", "get_arg": "forwarding_rule", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("addresses", "global"): {"asset_type": "compute.googleapis.com/Address", "client_attr": "global_addresses", "get_arg": "address", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("sslCertificates", "global"): {"asset_type": "compute.googleapis.com/SslCertificate", "client_attr": "ssl_certificates", "get_arg": "ssl_certificate", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("targetHttpsProxies", "global"): {"asset_type": "compute.googleapis.com/TargetHttpsProxy", "client_attr": "target_https_proxies", "get_arg": "target_https_proxy", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("urlMaps", "global"): {"asset_type": "compute.googleapis.com/UrlMap", "client_attr": "url_maps", "get_arg": "url_map", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("snapshots", "global"): {"asset_type": "compute.googleapis.com/Snapshot", "client_attr": "snapshots", "get_arg": "snapshot", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("targetHttpProxies", "global"): {"asset_type": "compute.googleapis.com/TargetHttpProxy", "client_attr": "target_http_proxies", "get_arg": "target_http_proxy", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("machineImages", "global"): {"asset_type": "compute.googleapis.com/MachineImage", "client_attr": "machine_images", "get_arg": "machine_image", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("images", "global"): {"asset_type": "compute.googleapis.com/Image", "client_attr": "images", "get_arg": "image", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("externalVpnGateways", "global"): {"asset_type": "compute.googleapis.com/ExternalVpnGateway", "client_attr": "external_vpn_gateways", "get_arg": "external_vpn_gateway", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("networks", "global"): {"asset_type": "compute.googleapis.com/Network", "client_attr": "networks", "get_arg": "network", "set_labels_request_cls": None, "set_labels_method": None, "set_labels_arg_name": None},
    }

    def _resolve_key(self, event: AuditLogEvent):
        # 1. Normalize method name
        method = event.method_name.replace("compute.", "").replace("beta.", "").replace("v1.", "")
        
        # 2. Direct mapping for regional/zonal disks
        if "regionDisks.insert" in method:
            return ("disks", "regions")
        if "disks.insert" in method:
            return ("disks", "zones")
            
        # 3. Fallback regex for other insert methods
        match = re.match(r'(?:region|zone|global)?([A-Za-z]+)\.insert', method)
        if match:
            collection = (match.group(1)[0].lower() + match.group(1)[1:]) + "s"
            scope = "global"
            if "/zones/" in event.resource_name: scope = "zones"
            elif "/regions/" in event.resource_name: scope = "regions"
                
            key = (collection, scope)
            return key if key in self.SERVICE_REGISTRY else None
            
        return None

    def supports(self, event: AuditLogEvent) -> bool:
        return event.service_name == self.SERVICE and self._resolve_key(event) is not None

    def classify(self, event: AuditLogEvent) -> ResourceEvent:
        key = self._resolve_key(event)
        metadata = self.SERVICE_REGISTRY[key]
        return ResourceEvent(
            project_id=event.project_id,
            asset_type=metadata["asset_type"],
            resource_name=event.resource_name,
            service_name=event.service_name,
            method_name=event.method_name,
            location=event.location,
        )
