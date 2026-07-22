# ==============================================================================
# RESOURCES THAT FULLY SUPPORT GCP LABELS (100% Implemented)
# ==============================================================================
SUPPORTED_LABEL_RESOURCES = {
    "aiplatform.googleapis.com/Dataset",
    "aiplatform.googleapis.com/Model",
    "alloydb.googleapis.com/Cluster",
    "alloydb.googleapis.com/Instance",
    "appengine.googleapis.com/Application",
    "appengine.googleapis.com/Version",
    "artifactregistry.googleapis.com/Repository",
    "bigquery.googleapis.com/Dataset",
    "bigquery.googleapis.com/Table",
    "bigquery.googleapis.com/Model",
    "cloudfunctions.googleapis.com/CloudFunction",
    "cloudfunctions.googleapis.com/Function",
    "cloudkms.googleapis.com/CryptoKey",
    "cloudresourcemanager.googleapis.com/Project",
    "compute.googleapis.com/Address",
    "compute.googleapis.com/Disk",
    "compute.googleapis.com/ForwardingRule",
    "compute.googleapis.com/Image",
    "compute.googleapis.com/Instance",
    "compute.googleapis.com/MachineImage",
    "compute.googleapis.com/Snapshot",
    "compute.googleapis.com/BackendService",
    "compute.googleapis.com/HealthCheck",
    "compute.googleapis.com/SslCertificate",
    "compute.googleapis.com/TargetHttpProxy",
    "compute.googleapis.com/TargetHttpsProxy",
    "compute.googleapis.com/UrlMap",
    "container.googleapis.com/Cluster",
    "dataform.googleapis.com/Repository",
    "dataplex.googleapis.com/DataScan",
    "dataplex.googleapis.com/EntryGroup",
    "dns.googleapis.com/ManagedZone",
    "monitoring.googleapis.com/AlertPolicy",
    "pubsub.googleapis.com/Subscription",
    "pubsub.googleapis.com/Topic",
    "redis.googleapis.com/Instance",
    "run.googleapis.com/Service",
    "secretmanager.googleapis.com/Secret",
    "sqladmin.googleapis.com/Instance",
    "storage.googleapis.com/Bucket",
}

# ==============================================================================
# RESOURCES THAT ONLY SUPPORT GCP TAGS (Safely Bypassed for Now)
# ==============================================================================
SUPPORTED_TAG_RESOURCES = {
    "compute.googleapis.com/ExternalVpnGateway",
    "compute.googleapis.com/Firewall",
    "compute.googleapis.com/Network",
    "compute.googleapis.com/Route",
    "compute.googleapis.com/Router",
    "compute.googleapis.com/Subnetwork",
    "compute.googleapis.com/TargetPool",
    "compute.googleapis.com/TargetVpnGateway",
    "compute.googleapis.com/VpnGateway",
    "compute.googleapis.com/VpnTunnel",
}


















# SUPPORTED_LABEL_RESOURCES = {
#     # Resources that support BOTH Labels and Tags
#     "compute.googleapis.com/Instance",
#     "compute.googleapis.com/Disk",
#     "compute.googleapis.com/Snapshot",
#     "compute.googleapis.com/Image",
#     "compute.googleapis.com/ForwardingRule",
#     "compute.googleapis.com/ExternalVpnGateway",
#     "compute.googleapis.com/TargetVpnGateway",
#     "compute.googleapis.com/VpnGateway",
#     "compute.googleapis.com/VpnTunnel",
#     "compute.googleapis.com/Router",
    
#     # Resources that support ONLY Labels
#     "compute.googleapis.com/Address",
#     "compute.googleapis.com/MachineImage",

#     # BIGQUERY
#     "bigquery.googleapis.com/Dataset",
#     "bigquery.googleapis.com/Table",
#     "bigquery.googleapis.com/Model",

#     # Storage Bucket
#     "storage.googleapis.com/Bucket",

#     "cloudresourcemanager.googleapis.com/Project",
#     "cloudkms.googleapis.com/CryptoKey",

#     "pubsub.googleapis.com/Topic",
#     "pubsub.googleapis.com/Subscription",
#     "sqladmin.googleapis.com/Instance",

#     "container.googleapis.com/Cluster",
#     "run.googleapis.com/Service",

#     "artifactregistry.googleapis.com/Repository",
#     "cloudfunctions.googleapis.com/Function",
#     "cloudfunctions.googleapis.com/CloudFunction", # Covers v1 and v2

#     "aiplatform.googleapis.com/Dataset",
#     "aiplatform.googleapis.com/Model",
#     "aiplatform.googleapis.com/CustomJob",
#     "aiplatform.googleapis.com/PipelineJob",
#     "aiplatform.googleapis.com/BatchPredictionJob",
#     "dataplex.googleapis.com/EntryGroup",
#     "dataplex.googleapis.com/DataScan",


#     "appengine.googleapis.com/Application",
#     "redis.googleapis.com/Instance",

#     "monitoring.googleapis.com/AlertPolicy",
#     "dataform.googleapis.com/Repository",
#     "dns.googleapis.com/ManagedZone",
#     "alloydb.googleapis.com/Cluster",
#     "alloydb.googleapis.com/Instance",

#     # "container.googleapis.com/Cluster",
#     # "container.googleapis.com/NodePool",
#     # "secretmanager.googleapis.com/Secret",


#     # "apikeys.googleapis.com/Key",
#     # "appengine.googleapis.com/Application",
#     # "appengine.googleapis.com/Service",
#     # "appengine.googleapis.com/Version",
#     # "cloudfunctions.googleapis.com/Function",
# }

# SUPPORTED_TAG_RESOURCES = {
#     # Resources that support ONLY Tags
#     "compute.googleapis.com/Network",
#     "compute.googleapis.com/Subnetwork",
#     "compute.googleapis.com/Firewall",
#     "compute.googleapis.com/SecurityPolicy",
#     "compute.googleapis.com/HealthCheck",
#     "compute.googleapis.com/BackendService",
#     "compute.googleapis.com/NetworkEndpointGroup",
#     "compute.googleapis.com/TargetHttpsProxy",
#     "compute.googleapis.com/TargetHttpProxy",
#     "compute.googleapis.com/UrlMap",
#     "compute.googleapis.com/InstanceGroup",
#     "compute.googleapis.com/SslPolicy",
#     "compute.googleapis.com/TargetPool",
#     "compute.googleapis.com/SslCertificate",
#     "compute.googleapis.com/NetworkAttachment",
#     "compute.googleapis.com/ServiceAttachment",
    
#     # resource types after verification.
#     # "pubsub.googleapis.com/Topic",
#     # "compute.googleapis.com/ForwardingRule",


# }