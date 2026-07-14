from flask import jsonify

from registry.reader import RegistryReader
from config import REGISTRY_BUCKET


def health():

    applications = RegistryReader().load_all()

    products = sorted(
        {
            application["product"]
            for application in applications
        }
    )

    project_ids = sorted(
        {
            binding["projectId"]
            for application in applications
            for binding in application["bindings"]
            if binding["cloud"] == "gcp"
        }
    )

    return jsonify(
        {
            "service": "metadata-governance",
            "status": "healthy",
            "registry": {
                "source": "Cloud Storage",
                "bucket": REGISTRY_BUCKET,
                "applications": len(applications),
                "products": len(products),
                "projects": len(project_ids),
                "bindings": len(project_ids),
            },
            "product_names": products,
            "project_ids": project_ids,
        }
    )