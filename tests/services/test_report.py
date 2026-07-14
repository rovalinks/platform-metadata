from unittest.mock import patch

from services.report import ReportService


@patch("services.report.EnforcementService")
@patch("services.report.ComplianceService")
def test_report(
    mock_compliance_cls,
    mock_enforcement_cls,
    mocker,
):
    mock_repository = mocker.Mock()

    mock_discovery = mocker.Mock()
    mock_discovery.discover.return_value = [1, 2, 3]

    mock_compliance = mocker.Mock()
    mock_compliance.evaluate.return_value = [
        mocker.Mock(compliant=True),
        mocker.Mock(compliant=False),
        mocker.Mock(compliant=True),
    ]
    mock_compliance_cls.return_value = mock_compliance

    mock_enforcement = mocker.Mock()
    mock_enforcement.plan.return_value = [
        {"resource": "vm"}
    ]
    mock_enforcement_cls.return_value = mock_enforcement

    service = ReportService(
        mock_repository,
        mock_discovery,
    )

    report = service.report("test-project")

    assert report.total_resources == 3
    assert report.supported_resources == 3
    assert report.compliant_resources == 2
    assert report.non_compliant_resources == 1
    assert report.enforcement_candidates == 1