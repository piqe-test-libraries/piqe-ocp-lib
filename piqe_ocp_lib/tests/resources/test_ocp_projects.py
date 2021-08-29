import logging

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpProjects

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="class")
def setup_params(get_kubeconfig):
    params_dict = {
        "project_api_obj": OcpProjects(kube_config_file=get_kubeconfig),
        "project1": {"name": "test-project1", "label": {"test": "1", "css-test": "True"}},
        "project2": {"name": "test-project2", "label": {"test": "2", "css-test": "True"}},
        "project3": {"name": "openshift-test1", "label": {"test": "3", "css-test": "True"}},
        "project4": {"name": "openshift-test2", "label": {"test": "4", "css-test": "True"}},
    }
    return params_dict


class TestOcpProjects:
    def test_create_a_project(self, setup_params):
        """
        1. Create a test project
        2. Verify that the name in the response
           object matches the name we used for the
           creation, that the response object is of
           the correct type and that it is in the
           active phase.
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.create_a_project(
            setup_params["project1"]["name"], labels_dict=setup_params["project1"]["label"]
        )
        assert api_response.kind == "Project"
        assert api_response.metadata.name == setup_params["project1"]["name"]
        assert api_response.status["phase"] == "Active"

    def test_create_namespace(self, setup_params):
        """
        1. Create a test namespace
        2. Verify that the name in the response
           object matches the name we used for the
           creation, that the response object is of
           the correct type and that it is in the
           active phase.
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.create_a_namespace(
            namespace_name=setup_params["project3"]["name"], labels_dict=setup_params["project3"]["label"]
        )
        logger.info("API Response : %s", api_response)
        assert api_response.kind == "Namespace"
        assert api_response.metadata.name == setup_params["project3"]["name"]
        assert api_response.status["phase"] == "Active"

    def test_label_a_project(self, setup_params):
        """
        1. Label our test project with a key value pair.
        2. Verify that the project has been in fact labeled
           by checking the metadata labels in the response
           object.
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.label_a_project(
            setup_params["project1"]["name"], setup_params["project1"]["label"]
        )
        assert api_response.kind == "Namespace"
        assert api_response.metadata.labels["test"] == setup_params["project1"]["label"]["test"]

    def test_create_and_label_a_project(self, setup_params):
        """
        1. Create a second test project, and this time label
           it on creation.
        2. Verify that the project has been created successfully
           and that in fact, it was labeled on creation
           by checking the metadata labels in the response
           object.
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.create_a_project(
            setup_params["project2"]["name"], labels_dict=setup_params["project2"]["label"]
        )
        assert api_response.kind == "Project"
        assert api_response.metadata.name == setup_params["project2"]["name"]
        created_project = project_api_obj.get_a_project(setup_params["project2"]["name"])
        assert created_project.kind == "Namespace"
        assert created_project.metadata.labels["test"] == setup_params["project2"]["label"]["test"]

    def test_create_and_label_a_namespace(self, setup_params):
        """
        1. Create a namespace and label them
        2. Verify that the namespace has been created successfully
           and that in fact, it was labeled on creation
           by checking the metadata labels in the response
           object.
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.create_a_namespace(
            setup_params["project4"]["name"], labels_dict=setup_params["project4"]["label"]
        )
        assert api_response.metadata.name == setup_params["project4"]["name"]
        created_project = project_api_obj.get_a_project(setup_params["project4"]["name"])
        assert created_project.metadata.labels["test"] == setup_params["project4"]["label"]["test"]

        # Cleanup
        logger.info("Cleanup Create and Label a Namespace.")
        logger.info("Delete the namespace.")
        api_response = project_api_obj.delete_a_namespace(setup_params["project4"]["name"])
        assert api_response.kind == "Namespace"
        assert api_response.status.phase == "Terminating"

    def test_get_a_project(self, setup_params):
        """
        1. Get both test projects created
        2. Verify that both response objects
           reflect the correct names and types.
        """
        project_api_obj = setup_params["project_api_obj"]
        project1 = project_api_obj.get_a_project(setup_params["project1"]["name"])
        project2 = project_api_obj.get_a_project(setup_params["project2"]["name"])
        assert project1.metadata.name == setup_params["project1"]["name"]
        assert project1.kind == "Namespace"
        assert project2.metadata.name == setup_params["project2"]["name"]
        assert project2.kind == "Namespace"

    def test_delete_a_project(self, setup_params):
        """
        1. Remove the two projects created in test_create_and_label_a_project
        2. Verify the response kind.
        3 Verify the state transition to terminating.

        :param setup_params:
        :return:
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.delete_a_project(setup_params["project1"]["name"])
        assert api_response.kind == "Namespace"
        assert api_response.status.phase == "Terminating"

        api_response = project_api_obj.delete_a_project(setup_params["project2"]["name"])
        assert api_response.kind == "Namespace"
        assert api_response.status.phase == "Terminating"

    def test_delete_a_namespace(self, setup_params):
        """
        1. Delete a namespace
        2. Verify the response kind.
        3 Verify the state transition to terminating.

        :param setup_params: (dict)
        :return: None
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.delete_a_namespace(setup_params["project3"]["name"])
        assert api_response.kind == "Namespace"
        assert api_response.status.phase == "Terminating"

    def test_get_all_projects(self, setup_params):
        """
        1. Get all projects and determine the count.
        2. Create another project.
        3. Get all projects, determine the updated count and assert that it equals the original plus 1.
        4. Delete the created project, get all projects and assert that the original and final counts
           are equal.

        :param setup_params:
        :return:
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.get_all_projects()
        original_project_count = len(api_response.items)

        create_project_response = project_api_obj.create_a_project(
            setup_params["project1"]["name"], labels_dict=setup_params["project1"]["label"]
        )
        assert create_project_response.status.phase == "Active"

        updated_api_response = project_api_obj.get_all_projects()
        updated_project_count = len(updated_api_response.items)
        assert updated_project_count == (original_project_count + 1)

        delete_project_response = project_api_obj.delete_a_project(setup_params["project1"]["name"])
        assert delete_project_response.status.phase == "Terminating"

        final_api_response = project_api_obj.get_all_projects()
        final_project_count = len(final_api_response.items)
        assert final_project_count == original_project_count

    def test_does_project_exist(self, setup_params):
        """
        1. Create a project and validate that does_project_exist returns True.
        2. Delete the project and validate that does_project_exist returns False.
        :param setup_params:
        :return:
        """
        project_api_obj = setup_params["project_api_obj"]

        project_name = setup_params["project1"]["name"]
        project_label = setup_params["project1"]["label"]
        project_api_obj.create_a_project(project_name=project_name, labels_dict=project_label)
        is_created_project_present = project_api_obj.does_project_exist(project_name)
        assert is_created_project_present is True

        project_api_obj.delete_a_project(project_name=project_name)
        is_deleted_project_present = project_api_obj.does_project_exist(project_name)
        assert is_deleted_project_present is False
