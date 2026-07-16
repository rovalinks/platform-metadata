from google.cloud import compute_v1
from google.api_core.exceptions import PreconditionFailed
import logging
from clients.base import ResourceClient
from models.resource import Resource
import config
from utils.labels import reconcile_labels

logger = logging.getLogger(__name__)

class ComputeClient(ResourceClient):
    REGISTRY = {
        ("instances", "zones"): {"asset_type": "compute.googleapis.com/Instance", "client_attr": "instances", "get_arg": "instance", "set_arg": "instance", "set_labels_request_cls": compute_v1.InstancesSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "instances_set_labels_request_resource"},
        ("disks", "zones"): {"asset_type": "compute.googleapis.com/Disk", "client_attr": "disks", "get_arg": "disk", "set_arg": "resource", "set_labels_request_cls": compute_v1.ZoneSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "zone_set_labels_request_resource"},
        ("disks", "regions"): {"asset_type": "compute.googleapis.com/Disk", "client_attr": "region_disks", "get_arg": "disk", "set_arg": "resource", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("addresses", "regions"): {"asset_type": "compute.googleapis.com/Address", "client_attr": "addresses", "get_arg": "address", "set_arg": "resource", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("addresses", "global"): {"asset_type": "compute.googleapis.com/Address", "client_attr": "global_addresses", "get_arg": "address", "set_arg": "resource", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        ("forwardingRules", "regions"): {"asset_type": "compute.googleapis.com/ForwardingRule", "client_attr": "forwarding_rules", "get_arg": "forwarding_rule", "set_arg": "resource", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        ("forwardingRules", "global"): {"asset_type": "compute.googleapis.com/ForwardingRule", "client_attr": "global_forwarding_rules", "get_arg": "forwarding_rule", "set_arg": "resource", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},

        # ("networkEndpointGroups", "zones"): {"asset_type": "compute.googleapis.com/NetworkEndpointGroup", "client_attr": "network_endpoint_groups", "get_arg": "network_endpoint_group", "set_labels_request_cls": compute_v1.ZoneSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "zone_set_labels_request_resource"},
        # ("instanceGroups", "zones"): {"asset_type": "compute.googleapis.com/InstanceGroup", "client_attr": "instance_groups", "get_arg": "instance_group", "set_labels_request_cls": compute_v1.ZoneSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "zone_set_labels_request_resource"},
        # ("resourcePolicies", "regions"): {"asset_type": "compute.googleapis.com/ResourcePolicy", "client_attr": "resource_policies", "get_arg": "resource_policy", "set_labels_request_cls": None, "set_labels_method": None, "set_labels_arg_name": None},
        # ("subnetworks", "regions"): {"asset_type": "compute.googleapis.com/Subnetwork", "client_attr": "subnetworks", "get_arg": "subnetwork", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("healthChecks", "regions"): {"asset_type": "compute.googleapis.com/HealthCheck", "client_attr": "region_health_checks", "get_arg": "health_check", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("backendServices", "regions"): {"asset_type": "compute.googleapis.com/BackendService", "client_attr": "region_backend_services", "get_arg": "backend_service", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("sslCertificates", "regions"): {"asset_type": "compute.googleapis.com/SslCertificate", "client_attr": "region_ssl_certificates", "get_arg": "ssl_certificate", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("targetHttpsProxies", "regions"): {"asset_type": "compute.googleapis.com/TargetHttpsProxy", "client_attr": "region_target_https_proxies", "get_arg": "target_https_proxy", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("urlMaps", "regions"): {"asset_type": "compute.googleapis.com/UrlMap", "client_attr": "region_url_maps", "get_arg": "url_map", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("targetHttpProxies", "regions"): {"asset_type": "compute.googleapis.com/TargetHttpProxy", "client_attr": "region_target_http_proxies", "get_arg": "target_http_proxy", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("instanceGroups", "regions"): {"asset_type": "compute.googleapis.com/InstanceGroup", "client_attr": "region_instance_groups", "get_arg": "instance_group", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("vpnTunnels", "regions"): {"asset_type": "compute.googleapis.com/VpnTunnel", "client_attr": "vpn_tunnels", "get_arg": "vpn_tunnel", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("vpnGateways", "regions"): {"asset_type": "compute.googleapis.com/VpnGateway", "client_attr": "vpn_gateways", "get_arg": "vpn_gateway", "set_labels_request_cls": compute_v1.RegionSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "region_set_labels_request_resource"},
        # ("healthChecks", "global"): {"asset_type": "compute.googleapis.com/HealthCheck", "client_attr": "health_checks", "get_arg": "health_check", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("backendServices", "global"): {"asset_type": "compute.googleapis.com/BackendService", "client_attr": "backend_services", "get_arg": "backend_service", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},  
        # ("sslCertificates", "global"): {"asset_type": "compute.googleapis.com/SslCertificate", "client_attr": "ssl_certificates", "get_arg": "ssl_certificate", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("targetHttpsProxies", "global"): {"asset_type": "compute.googleapis.com/TargetHttpsProxy", "client_attr": "target_https_proxies", "get_arg": "target_https_proxy", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("urlMaps", "global"): {"asset_type": "compute.googleapis.com/UrlMap", "client_attr": "url_maps", "get_arg": "url_map", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("snapshots", "global"): {"asset_type": "compute.googleapis.com/Snapshot", "client_attr": "snapshots", "get_arg": "snapshot", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("targetHttpProxies", "global"): {"asset_type": "compute.googleapis.com/TargetHttpProxy", "client_attr": "target_http_proxies", "get_arg": "target_http_proxy", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("machineImages", "global"): {"asset_type": "compute.googleapis.com/MachineImage", "client_attr": "machine_images", "get_arg": "machine_image", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("images", "global"): {"asset_type": "compute.googleapis.com/Image", "client_attr": "images", "get_arg": "image", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("externalVpnGateways", "global"): {"asset_type": "compute.googleapis.com/ExternalVpnGateway", "client_attr": "external_vpn_gateways", "get_arg": "external_vpn_gateway", "set_labels_request_cls": compute_v1.GlobalSetLabelsRequest, "set_labels_method": "set_labels", "set_labels_arg_name": "global_set_labels_request_resource"},
        # ("networks", "global"): {"asset_type": "compute.googleapis.com/Network", "client_attr": "networks", "get_arg": "network", "set_labels_request_cls": None, "set_labels_method": None, "set_labels_arg_name": None},
    }
    
SUPPORTED_LABEL_TYPES = {meta["asset_type"] for meta in REGISTRY.values() if meta.get("set_labels_request_cls") is not None}
    
    def __init__(self):
        self.zone_operations = compute_v1.ZoneOperationsClient()
        self.region_operations = compute_v1.RegionOperationsClient()
        self.global_operations = compute_v1.GlobalOperationsClient()
        self.instances = compute_v1.InstancesClient()
        self.disks = compute_v1.DisksClient()
        self.region_disks = compute_v1.RegionDisksClient()
        self.addresses = compute_v1.AddressesClient()
        self.global_addresses = compute_v1.GlobalAddressesClient()
        self.forwarding_rules = compute_v1.ForwardingRulesClient()
        self.global_forwarding_rules = compute_v1.GlobalForwardingRulesClient() 


        # self.resource_policies = compute_v1.ResourcePoliciesClient()
        # self.snapshots = compute_v1.SnapshotsClient()
        # self.images = compute_v1.ImagesClient()
        # self.machine_images = compute_v1.MachineImagesClient()
        # self.networks = compute_v1.NetworksClient()
        # self.subnetworks = compute_v1.SubnetworksClient()
        # self.firewalls = compute_v1.FirewallsClient()
        # self.routers = compute_v1.RoutersClient()
        # self.network_attachments = compute_v1.NetworkAttachmentsClient()
        # self.service_attachments = compute_v1.ServiceAttachmentsClient()
        # self.vpn_gateways = compute_v1.VpnGatewaysClient()
        # self.vpn_tunnels = compute_v1.VpnTunnelsClient()
        # self.target_vpn_gateways = compute_v1.TargetVpnGatewaysClient()
        # self.external_vpn_gateways = compute_v1.ExternalVpnGatewaysClient()
        # self.packet_mirrorings = compute_v1.PacketMirroringsClient()
        # self.target_pools = compute_v1.TargetPoolsClient()
        # self.ssl_certificates = compute_v1.SslCertificatesClient()
        # self.region_ssl_certificates = compute_v1.RegionSslCertificatesClient()
        # self.ssl_policies = compute_v1.SslPoliciesClient()
        # self.target_http_proxies = compute_v1.TargetHttpProxiesClient()
        # self.region_target_http_proxies = compute_v1.RegionTargetHttpProxiesClient()
        # self.target_https_proxies = compute_v1.TargetHttpsProxiesClient()
        # self.region_target_https_proxies = compute_v1.RegionTargetHttpsProxiesClient()
        # self.url_maps = compute_v1.UrlMapsClient()
        # self.region_url_maps = compute_v1.RegionUrlMapsClient()
        # self.backend_services = compute_v1.BackendServicesClient()
        # self.region_backend_services = compute_v1.RegionBackendServicesClient()
        # self.health_checks = compute_v1.HealthChecksClient()
        # self.region_health_checks = compute_v1.RegionHealthChecksClient()
        # self.network_endpoint_groups = compute_v1.NetworkEndpointGroupsClient()
        # self.instance_groups = compute_v1.InstanceGroupsClient()
        # self.region_instance_groups = compute_v1.RegionInstanceGroupsClient()
        # self.instance_templates = compute_v1.InstanceTemplatesClient()
        # self.instance_group_managers = compute_v1.InstanceGroupManagersClient()
        # self.region_instance_group_managers = compute_v1.RegionInstanceGroupManagersClient()
        # self.security_policies = compute_v1.SecurityPoliciesClient()

    def supports(self, a): return a.startswith("compute.googleapis.com/")
    
    def supports_labels(self, a): return a in self.SUPPORTED_LABEL_TYPES
    
    def _parse_resource_url(self, u):
        if "//compute.googleapis.com/" in u: u = u.split("//compute.googleapis.com/")[1]
        if "projects/" in u: u = u[u.find("projects/"):]
        p = u.strip("/").split("/")
        proj, scope = p[1], p[2]
        if scope in ("zones", "regions"):
            return {"project": proj, "scope_type": scope, "scope_value": p[3], "resource_type": p[4], "name": p[5]}
        return {"project": proj, "scope_type": "global", "scope_value": "global", "resource_type": p[3], "name": p[4]}
    
    def labels(self, r: Resource):
        try:
            if not self.supports_labels(r.asset_type): return None
            info = self._parse_resource_url(r.name)
            entry = self.REGISTRY.get((info["resource_type"], info["scope_type"]))
            if not entry: return None
            client = getattr(self, entry["client_attr"], None)
            kwargs = {"project": info["project"], entry["get_arg"]: info["name"]}
            if info["scope_type"] in ("zones", "regions"): kwargs["zone" if info["scope_type"] == "zones" else "region"] = info["scope_value"]
            return dict(getattr(client.get(**kwargs), "labels", {}))
        except Exception as e:
            logger.exception("Failed to fetch labels: %s", e); return None
            
    def get(self, n: str) -> Resource:
        try:
            info = self._parse_resource_url(n)
            entry = self.REGISTRY.get((info["resource_type"], info["scope_type"]))
            if not entry: return None
            client = getattr(self, entry["client_attr"], None)
            kwargs = {"project": info["project"], entry["get_arg"]: info["name"]}
            if info["scope_type"] in ("zones", "regions"): kwargs["zone" if info["scope_type"] == "zones" else "region"] = info["scope_value"]
            res = client.get(**kwargs)
            return Resource(asset_type=entry["asset_type"], name=n, project=info["project"], location=info["scope_value"], labels=dict(getattr(res, "labels", {})))
        except Exception as e:
            logger.exception("Failed to get resource %s: %s", n, e); return None
        
    def _apply_labels_generic(self, g, s, req_cls, labels):
        def run():
            res = g()
            ex = dict(getattr(res, "labels", {}))
            # Use reconcile_labels to merge safely while keeping existing labels[cite: 11]
            m = reconcile_labels(ex, labels)
            if m == ex: return True
            # Include fingerprint for optimistic locking requirement[cite: 11]
            return s(req_cls(labels=m, label_fingerprint=res.label_fingerprint))
        try: return run()
        except PreconditionFailed: return run()
        
    def apply_labels(self, res, labels: dict):
        info = self._parse_resource_url(res.name)
        entry = self.REGISTRY.get((info["resource_type"], info["scope_type"]))
        if not entry or not entry.get("set_labels_request_cls"): return True
        client = getattr(self, entry["client_attr"], None)
        meth = getattr(client, entry["set_labels_method"])
        scope_arg = {"zone" if info["scope_type"] == "zones" else "region": info["scope_value"]} if info["scope_type"] in ("zones", "regions") else {}
        
        def get_r():
            kwargs = {"project": info["project"], entry["get_arg"]: info["name"]}
            kwargs.update(scope_arg)
            return client.get(**kwargs)
            
        def set_r(req):
            set_target = entry.get("set_arg", entry["get_arg"]) 
            kwargs = {"project": info["project"], set_target: info["name"]}
            kwargs.update(scope_arg)
            kwargs[entry["set_labels_arg_name"]] = req
            return meth(**kwargs)
            
        op = self._apply_labels_generic(get_r, set_r, entry["set_labels_request_cls"], labels)
        if op and op is not True:
            if info["scope_type"] == "zones": self.zone_operations.wait(project=info["project"], zone=info["scope_value"], operation=op.name)
            elif info["scope_type"] == "regions": self.region_operations.wait(project=info["project"], region=info["scope_value"], operation=op.name)
            else: self.global_operations.wait(project=info["project"], operation=op.name)
        return True