import logging

logger = logging.getLogger(__name__)


def _normalize(resource_name: str) -> str:
    if resource_name.startswith("//compute.googleapis.com/"):
        return resource_name[len("//compute.googleapis.com/"):]
    return resource_name


def parse_instance_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "zone": parts[3],
        "instance": parts[5],
    }


def parse_disk_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "zone": parts[3],
        "disk": parts[5],
    }


def parse_address_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "address": parts[5],
    }


def parse_forwarding_rule_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "forwarding_rule": parts[5],
    }


def parse_subnetwork_name(resource_name: str):
    logger.info("Parsing subnetwork: %s", resource_name)

    resource_name = _normalize(resource_name)

    parts = resource_name.split("/")

    logger.info("Split parts: %s", parts)

    result = {
        "project": parts[1],
        "region": parts[3],
        "subnetwork": parts[5],
    }

    logger.info("Parsed result: %s", result)

    return result


def parse_health_check_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "health_check": parts[4],
    }


def parse_backend_service_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "backend_service": parts[4],
    }


def parse_network_endpoint_group_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "zone": parts[3],
        "network_endpoint_group": parts[5],
    }


def parse_firewall_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "firewall": parts[4],
    }


def parse_network_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "network": parts[4],
    }


def parse_snapshot_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "snapshot": parts[4],
    }


def parse_image_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "image": parts[4],
    }


def parse_machine_image_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "machine_image": parts[4],
    }


def parse_ssl_certificate_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "ssl_certificate": parts[4],
    }


def parse_ssl_policy_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "ssl_policy": parts[4],
    }


def parse_target_http_proxy_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "target_http_proxy": parts[4],
    }


def parse_target_https_proxy_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "target_https_proxy": parts[4],
    }


def parse_url_map_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "url_map": parts[4],
    }


def parse_router_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "router": parts[5],
    }


def parse_instance_group_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "zone": parts[3],
        "instance_group": parts[5],
    }


def parse_instance_group_manager_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "zone": parts[3],
        "instance_group_manager": parts[5],
    }


def parse_instance_template_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "instance_template": parts[4],
    }


def parse_target_pool_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "target_pool": parts[5],
    }


def parse_resource_policy_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "resource_policy": parts[5],
    }


def parse_target_vpn_gateway_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "target_vpn_gateway": parts[5],
    }


def parse_network_attachment_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "network_attachment": parts[5],
    }


def parse_service_attachment_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "service_attachment": parts[5],
    }


def parse_vpn_gateway_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "vpn_gateway": parts[5],
    }


def parse_packet_mirroring_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "packet_mirroring": parts[5],
    }


def parse_external_vpn_gateway_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "external_vpn_gateway": parts[4],
    }


def parse_http_health_check_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "http_health_check": parts[4],
    }


def parse_vpn_tunnel_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "region": parts[3],
        "vpn_tunnel": parts[5],
    }


def parse_security_policy_name(resource_name: str):
    parts = _normalize(resource_name).split("/")
    return {
        "project": parts[1],
        "security_policy": parts[4],
    }