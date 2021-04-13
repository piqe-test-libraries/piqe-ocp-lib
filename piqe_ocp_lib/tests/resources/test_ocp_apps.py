import json
from random import randint

from openshift.dynamic.client import ResourceInstance
import pytest

from piqe_ocp_lib.api.resources import OcpApps, OcpBase, OcpProjects, OcpTemplates


@pytest.fixture(scope="class")
def setup_params(get_kubeconfig):
    params_dict = {}
    params_dict["app_api_obj"] = OcpApps(kube_config_file=get_kubeconfig)
    params_dict["project_api_obj"] = OcpProjects(kube_config_file=get_kubeconfig)
    params_dict["template_api_obj"] = OcpTemplates(kube_config_file=get_kubeconfig)
    params_dict["test_project"] = "app-project"
    params_dict["ident"] = randint(0, 10)
    params_dict["test_app_params"] = {"MEMORY_LIMIT": "768Mi"}
    params_dict["template_name"] = "httpd-example"
    base_api = OcpBase(kube_config_file=get_kubeconfig)
    dyn_client = base_api.dyn_client
    params_dict["v1_deploymentconfig"] = dyn_client.resources.get(api_version="v1", kind="DeploymentConfig")
    return params_dict


class TestOcpApps(object):
    def test_create_app_from_template(self, setup_params):
        """
        1. Create a test project
        2. Add a template to it
        3. Create an app from the added template
           by name in the same test project
        4. Verify that the app was created by checking
           its resource names and compare them to the
           expected naming convention.
        """
        app_api_obj = setup_params["app_api_obj"]
        project_api_obj = setup_params["project_api_obj"]
        template_api_obj = setup_params["template_api_obj"]
        project_api_obj.create_a_project(setup_params["test_project"])
        with open("piqe_ocp_lib/tests/resources/templates/httpd.json") as t:
            body = json.load(t)
        template_api_obj.create_a_template_in_a_namespace(body, project=setup_params["test_project"])

        res, _ = app_api_obj.create_app_from_template(
            setup_params["test_project"],
            setup_params["template_name"],
            setup_params["ident"],
            setup_params["test_app_params"],
            template_location=setup_params["test_project"],
        )

        for resource in res:
            assert resource.metadata.name == setup_params["template_name"] + "-" + str(setup_params["ident"])

    def test_delete_template_based_app(self, setup_params):
        """
        1. Delete the app we created in our test project
        2. Verify the deletion by checking that the response
           is not None, but instead that it is of type: ResourceInstance.
        """
        app_api_obj = setup_params["app_api_obj"]

        res = app_api_obj.delete_template_based_app(
            setup_params["test_project"],
            setup_params["template_name"],
            setup_params["ident"],
            setup_params["test_app_params"],
            template_location=setup_params["test_project"],
        )

        for resource in res:
            assert isinstance(resource, ResourceInstance)

        # Cleanup - Remove the project that was created within test_create_app_from_template.
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.delete_a_project(setup_params["test_project"])
        assert api_response.kind == "Namespace"
        assert api_response.status.phase == "Terminating"
