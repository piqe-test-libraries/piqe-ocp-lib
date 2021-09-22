import json
from pathlib import Path

import pytest

from piqe_ocp_lib.api.resources import OcpApps, OcpProjects, OcpServices, OcpTemplates


@pytest.fixture(scope="module")
def ocp_services(get_kubeconfig) -> OcpServices:
    return OcpServices(get_kubeconfig)


@pytest.fixture(scope="module")
def ocp_project(get_kubeconfig) -> OcpProjects:
    return OcpProjects(get_kubeconfig)


@pytest.fixture(scope="module")
def ocp_template(get_kubeconfig) -> OcpTemplates:
    return OcpTemplates(get_kubeconfig)


@pytest.fixture(scope="module")
def ocp_app(get_kubeconfig) -> OcpApps:
    return OcpApps(get_kubeconfig)


@pytest.fixture(scope="module")
def httpd_template() -> str:
    path = Path(__file__).parent / "templates/httpd.json"

    with open(path) as file:
        yield json.load(file)


@pytest.fixture
def project(ocp_project) -> str:
    project_name = "test-services"
    project_label = {"css-test": "True"}
    ocp_project.create_a_project(project_name=project_name, labels_dict=project_label)

    yield project_name

    ocp_project.delete_a_project(project_name)


@pytest.fixture
def deploy_httpd_with_service(project, ocp_template, ocp_app, httpd_template):
    ocp_template.create_a_template_in_a_namespace(httpd_template, project=project)
    ocp_app.create_app_from_template(project, "httpd-example", 1, {}, project)


@pytest.mark.integration
@pytest.mark.positive
@pytest.mark.parametrize(
    "input,expected",
    [
        pytest.param(pytest.lazy_fixture("deploy_httpd_with_service"), 1, marks=pytest.mark.positive),
        pytest.param("", 0, marks=pytest.mark.negative),
    ],
)
def test_get_all_from_project(input, expected, project, ocp_services):
    result = ocp_services.get_all_from_project(project)
    assert len(result.items) == expected


@pytest.mark.integration
@pytest.mark.positive
@pytest.mark.usefixtures("deploy_httpd_with_service")
def test_get_app_ip_positive(project, ocp_services):
    expected = ocp_services.get_all_from_project(project).items[0].spec.clusterIP

    result = ocp_services.get_app_ip(project, "httpd-example-1")

    assert result == expected


@pytest.mark.integration
@pytest.mark.negative
def test_get_app_ip_negative(project, ocp_services):
    result = ocp_services.get_app_ip(project, "httpd-example-1")

    assert result is None
