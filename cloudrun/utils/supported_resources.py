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

    # Storage Bucket
    "storage.googleapis.com/Bucket",

    "cloudresourcemanager.googleapis.com/Project",
    "cloudkms.googleapis.com/CryptoKey",

    "pubsub.googleapis.com/Topic",
    "pubsub.googleapis.com/Subscription",
    "sqladmin.googleapis.com/Instance",

    "container.googleapis.com/Cluster",
    "run.googleapis.com/Service",

    "artifactregistry.googleapis.com/Repository",
    "cloudfunctions.googleapis.com/Function",
    "cloudfunctions.googleapis.com/CloudFunction", # Covers v1 and v2

    "aiplatform.googleapis.com/Dataset",
    "aiplatform.googleapis.com/Model",
    "aiplatform.googleapis.com/CustomJob",
    "aiplatform.googleapis.com/PipelineJob",
    "aiplatform.googleapis.com/BatchPredictionJob",
    "dataplex.googleapis.com/EntryGroup",
    "dataplex.googleapis.com/DataScan",

    # "container.googleapis.com/Cluster",
    # "container.googleapis.com/NodePool",
    # "secretmanager.googleapis.com/Secret",


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