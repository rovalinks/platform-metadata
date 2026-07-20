SUPPORTED_LABEL_RESOURCES = {
    # Resources that support BOTH Labels and Tags
    "compute.googleapis.com/Instance",
    "compute.googleapis.com/Disk",
    "compute.googleapis.com/Snapshot",
    "compute.googleapis.com/Image",
    "compute.googleapis.com/ForwardingRule",
    "compute.googleapis.com/ExternalVpnGateway",
    "compute.googleapis.com/TargetVpnGateway",
    "compute.googleapis.com/VpnGateway",
    "compute.googleapis.com/VpnTunnel",
    "compute.googleapis.com/Router",
    
    # Resources that support ONLY Labels
    "compute.googleapis.com/Address",
    "compute.googleapis.com/MachineImage",

    # BIGQUERY
    "bigquery.googleapis.com/Dataset",
    "bigquery.googleapis.com/Table",
    "bigquery.googleapis.com/Model",


    # "storage.googleapis.com/Bucket",
    # "bigquery.googleapis.com/Dataset",
    # "sqladmin.googleapis.com/Instance",
    # "artifactregistry.googleapis.com/Repository",
    #"pubsub.googleapis.com/Topic",
    # "container.googleapis.com/Cluster",
    # "container.googleapis.com/NodePool",
    # "secretmanager.googleapis.com/Secret",
    # "cloudresourcemanager.googleapis.com/Project",
    # "cloudkms.googleapis.com/CryptoKey",
    # "apikeys.googleapis.com/Key",
    # "appengine.googleapis.com/Application",
    # "appengine.googleapis.com/Service",
    # "appengine.googleapis.com/Version",
    # "cloudfunctions.googleapis.com/Function",
}

SUPPORTED_TAG_RESOURCES = {
    # Resources that support ONLY Tags
    "compute.googleapis.com/Network",
    "compute.googleapis.com/Subnetwork",
    "compute.googleapis.com/Firewall",
    "compute.googleapis.com/SecurityPolicy",
    "compute.googleapis.com/HealthCheck",
    "compute.googleapis.com/BackendService",
    "compute.googleapis.com/NetworkEndpointGroup",
    "compute.googleapis.com/TargetHttpsProxy",
    "compute.googleapis.com/TargetHttpProxy",
    "compute.googleapis.com/UrlMap",
    "compute.googleapis.com/InstanceGroup",
    "compute.googleapis.com/SslPolicy",
    "compute.googleapis.com/TargetPool",
    "compute.googleapis.com/SslCertificate",
    "compute.googleapis.com/NetworkAttachment",
    "compute.googleapis.com/ServiceAttachment",
    
    # resource types after verification.
    # "pubsub.googleapis.com/Topic",
    # "compute.googleapis.com/ForwardingRule",


}