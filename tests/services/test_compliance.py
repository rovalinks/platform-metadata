from models.resource import Resource
from services.compliance import ComplianceService


def test_compliance_success(mocker):

    mock_discovery = mocker.Mock()

    mock_discovery.discover.return_value = [
        Resource(
            asset_type="compute.googleapis.com/Instance",
            name="vm-01",
            project="platform-metadata-demo",
            labels={
                "application": "cpe-tagging-validation",
                "team": "cloud-platform-engineering",
                "owner": "camlong",
                "budgetowner": "pfernandez",
                "organization": "rba",
                "department": "cloud-platform-engineering",
                "costcenter": "placeholder",
                "environment": "sandbox",
                "businesscriticality": "low",
            },
        )
    ]

    mocker.patch(
        "services.governance.GovernanceService.expected_labels",
        return_value={
            "application": "cpe-tagging-validation",
            "team": "cloud-platform-engineering",
            "owner": "camlong",
            "budgetowner": "pfernandez",
            "organization": "rba",
            "department": "cloud-platform-engineering",
            "costcenter": "placeholder",
            "environment": "sandbox",
            "businesscriticality": "low",
        },
    )

    service = ComplianceService(mock_discovery)

    results = service.evaluate(
        "platform-metadata-demo"
    )

    assert len(results) == 1
    assert results[0].compliant
    assert results[0].missing_labels == []
    assert results[0].incorrect_labels == []

