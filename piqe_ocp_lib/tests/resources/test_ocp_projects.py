import logging

from kubernetes.client.rest import ApiException
import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api import ocp_exceptions
from piqe_ocp_lib.api.ocp_exception_handler import handle_exception
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
    def __setup(self, setup_params, project_name):
        """
        Performs common setup task of creating a project.

        :param setup_params:
        :param project_name:
        :return:
        """
        project_api_obj = setup_params["project_api_obj"]
        api_response = project_api_obj.create_a_project(project_name)
        assert api_response.metadata.name == project_name
        logger.info("Project : {}, succesfully created".format(api_response.metadata.name))

    def __cleanup(self, setup_params, project_name):
        """
        Performs common clean up task of deleting the specified project.

        :param setup_params: Dictionary containing the OcpBase
        :param project_name:
        :return:
        """
        project_api_obj = setup_params["project_api_obj"]
        if project_api_obj.does_project_exist(project_name):
            project_api_obj.delete_a_project(project_name)
            logger.info("Project : {}, successfully deleted".format(project_name))
        is_deleted_project_present = project_api_obj.does_project_exist(project_name)
        assert is_deleted_project_present is False

    def __log_exception_formatted(self, message, exception):
        """
        Provides consistent formatted logging of unexpected exceptions.

        :param message: String containing user specified error message.
        :param exception: The raised Exception
        :return:
        """
        logger.error(message)
        logger.error("Status: %s" % exception.status)
        logger.error("Reason: %s" % exception.reason)
        logger.error("  Body: %s" % exception.body.decode("utf-8"))

    def test_create_a_project(self, setup_params):
        """
        Positive path testing for create_a_project.
        Validates project creation by asserting project kind, metadata.name and status.
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            api_response = project_api_obj.create_a_project(
                setup_params["project1"]["name"], labels_dict=setup_params["project1"]["label"]
            )
            assert api_response.kind == "Project"
            assert api_response.metadata.name == setup_params["project1"]["name"]
            assert api_response.status["phase"] == "Active"
        except ApiException as e:
            err_msg = "Unexpected ApiException testing create_a_project!"
            self.__log_exception_formatted(err_msg, e)
            pytest.fail(err_msg)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_create_a_project_exception(self, setup_params):
        """
        Negative path testing of create_a_project to validate OcpException handling
        Validates that an OcpException is raised when an attempt is made to create a project that already exists.
        Validates that the correct exception: OcpResourceAlreadyExistsException is raised

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        self.__setup(setup_params, setup_params["project1"]["name"])

        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            project_api_obj.create_a_project(setup_params["project1"]["name"])
            # Fail the test if we fall through. Create operation should not have succeeded.
            pytest.fail("The expected OcpException was not thrown!")
        except ocp_exceptions.OcpResourceAlreadyExistsException:
            assert True

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_create_namespace(self, setup_params):
        """
        Positive path testing of create_a_namespace
        Validates namespace project creation by asserting project kind, metadata.name and status.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            api_response = project_api_obj.create_a_namespace(
                namespace_name=setup_params["project3"]["name"], labels_dict=setup_params["project3"]["label"]
            )
            assert api_response.kind == "Namespace"
            assert api_response.metadata.name == setup_params["project3"]["name"]
            assert api_response.status["phase"] == "Active"
        except ApiException as e:
            err_msg = "Unexpected ApiException testing create_a_namespace!"
            self.__log_exception_formatted(err_msg, e)
            pytest.fail(err_msg)
        #
        # Cleanup
        #
        #
        finally:
            self.__cleanup(setup_params, setup_params["project3"]["name"])

    def test_create_a_namespace_exception(self, setup_params):
        """
        Negative path testing of create_a_project to validate OcpException handling
        Validates that OcpResourceAlreadyExistsException is raised when an attempt is made
        to create a project that already exists.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            project_api_obj.create_a_namespace(namespace_name=setup_params["project2"]["name"])
        except ApiException:
            pytest.fail("Unexpected Exception testing create_a_namespace!")

        #
        # Execution
        #
        try:
            project_api_obj.create_a_namespace(setup_params["project2"]["name"])
            # Fail the test if we fall through. Create operation should not have succeeded.
            pytest.fail("The expected OcpException was not thrown!")
        except ocp_exceptions.OcpResourceAlreadyExistsException:
            assert True

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project2"]["name"])

    def test_label_a_project(self, setup_params):
        """
        Positive path testing of label_a_project
        Validates the label assignment by asserting project kind and metadata.label.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        project_name = setup_params["project1"]["name"]
        self.__setup(setup_params, project_name)

        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            api_response = project_api_obj.label_a_project(project_name, setup_params["project1"]["label"])
            assert api_response.kind == "Namespace"
            assert api_response.metadata.labels["test"] == setup_params["project1"]["label"]["test"]
        except ApiException as e:
            err_msg = "Unexpected ApiException testing label_a_project!"
            self.__log_exception_formatted(err_msg, e)
            pytest.fail(err_msg)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_label_a_project_exception(self, setup_params):
        """
        Negative path testing of exception handling
        Validates that the OcpInvalidParameterException is raised when an attempt
        is made to pass an invalid parameter to label the project.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        self.__setup(setup_params, setup_params["project1"]["name"])

        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            # Pass a string rather than a dictionary to trigger the exception.
            project_api_obj.label_a_project(setup_params["project1"]["name"], labels_dict="project1")
            # Fail the test if we fall through. Create operation should not have succeeded.
            pytest.fail("The expected OcpException was not thrown!")
        except ocp_exceptions.OcpInvalidParameterException:
            assert True

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_create_and_label_a_project(self, setup_params):
        """
        Positive path testing of create_and_label_a_project
        Validates project creation and that the label has been applied.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            api_response = project_api_obj.create_a_project(
                setup_params["project2"]["name"], labels_dict=setup_params["project2"]["label"]
            )
            assert api_response.kind == "Project"
            assert api_response.metadata.name == setup_params["project2"]["name"]
            created_project = project_api_obj.get_a_project(setup_params["project2"]["name"])
            assert created_project.kind == "Namespace"
            assert created_project.metadata.labels["test"] == setup_params["project2"]["label"]["test"]
        except ApiException as e:
            err_msg = "Unexpected ApiException testing create_and_label_a_project!"
            self.__log_exception_formatted(err_msg, e)
            pytest.fail(err_msg)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project2"]["name"])

    def test_create_and_label_a_project_exception(self, setup_params):
        """
        Negative path testing of exception handling
        Validates that the OcpInvalidParameterException is raised when an attempt
        is made to pass an invalid parameter to label the project.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            # Pass a string rather than a dictionary to trigger the exception.
            project_api_obj.create_a_project(setup_params["project1"]["name"], labels_dict="project1")
            # Fail the test if we fall through. Create operation should not have succeeded.
            pytest.fail("The expected OcpException was not thrown!")
        except ocp_exceptions.OcpInvalidParameterException:
            assert True

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_create_and_label_a_namespace(self, setup_params):
        """
        Positive path testing of create_and_label_a_namespace
        Validates namespace project creation and that the label has been applied.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            api_response = project_api_obj.create_a_namespace(
                setup_params["project4"]["name"], labels_dict=setup_params["project4"]["label"]
            )
            assert api_response.metadata.name == setup_params["project4"]["name"]
            created_project = project_api_obj.get_a_project(setup_params["project4"]["name"])
            assert created_project.metadata.labels["test"] == setup_params["project4"]["label"]["test"]
        except ApiException as e:
            message = "Unexpected ApiException testing create_and_label_a_namespace!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project4"]["name"])

    def test_create_and_label_a_namespace_exception(self, setup_params):
        """
        Negative path testing of exception handling
        Validates that the OcpInvalidParameterException is raised when an attempt
        is made to pass an invalid parameter to label the namespace.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            project_api_obj.create_a_namespace(setup_params["project2"]["name"], labels_dict="project2")
            # Fail the test if we fall through. Create operation should not have succeeded.
            pytest.fail("The expected OcpException was not thrown!")
        except ocp_exceptions.OcpInvalidParameterException:
            assert True

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project2"]["name"])

    def test_get_a_project(self, setup_params):
        """
        Positive poth test for get_a_project
        Validates that projects can be retrieved by name.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        self.__setup(setup_params, setup_params["project1"]["name"])
        self.__setup(setup_params, setup_params["project2"]["name"])

        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            project1 = project_api_obj.get_a_project(setup_params["project1"]["name"])
            project2 = project_api_obj.get_a_project(setup_params["project2"]["name"])
            assert project1.metadata.name == setup_params["project1"]["name"]
            assert project1.kind == "Namespace"
            assert project2.metadata.name == setup_params["project2"]["name"]
            assert project2.kind == "Namespace"
        except ApiException as e:
            message = "Unexpected ApiException testing get_a_project!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])
            self.__cleanup(setup_params, setup_params["project2"]["name"])

    def test_get_a_project_exception(self, setup_params):
        """
        Negative path testing of exception handling
        Validates that the OcpResourceNotFoundException is raised when an attempt
        is made to get a project that does not exist.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        project_name = setup_params["project1"]["name"]

        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            project_api_obj.get_a_project(project_name)
            # Fail the test if we fall through. Get operation should not have succeeded.
            pytest.fail("The expected OcpException was not thrown!")
        except ocp_exceptions.OcpResourceNotFoundException:
            assert True

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_delete_a_project(self, setup_params):
        """
        Positive path test to delete a project.
        Validates that a created project is deleted.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        self.__setup(setup_params, setup_params["project1"]["name"])

        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            project_api_obj.delete_a_project(setup_params["project1"]["name"])
            is_deleted_project_present = project_api_obj.does_project_exist(setup_params["project1"]["name"])
            assert is_deleted_project_present is False
        except ApiException as e:
            message = "Unexpected ApiException testing delete_a_project!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_delete_a_project_exception(self, setup_params):
        """
        Negative path testing of exception handling

        Validates that an OcpResourceNotFoundException is raised when an attempt
        is made to delete a project that doesn't exist.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_name = setup_params["project1"]["name"]
        project_api_obj = setup_params["project_api_obj"]
        try:
            project_api_obj.delete_a_project(project_name)
            # Fail the test if we fall through. Delete operation should not have succeeded.
            pytest.fail("Expected Exception was not thrown!")
        except ocp_exceptions.OcpResourceNotFoundException:
            assert True

    def test_delete_a_namespace(self, setup_params):
        """
        Positive path test for delete_a_namespace.
        Validates that the namespace project is deleted.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        project_api_obj = setup_params["project_api_obj"]
        project_api_obj.create_a_namespace(namespace_name=setup_params["project2"]["name"])

        #
        # Execution
        #
        try:
            project_api_obj.delete_a_namespace(setup_params["project2"]["name"])
            is_deleted_project_present = project_api_obj.does_project_exist(setup_params["project2"]["name"])
            assert is_deleted_project_present is False
        except ApiException as e:
            message = "Unexpected ApiException testing delete_a_namespace!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

    def test_delete_a_namespace_exception(self, setup_params):
        """
        Negative path testing of exception handling
        Validates that the OcpResourceNotFoundException is raised when an attempt
        is made to delete a namespace project that doesn't exist.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            project_api_obj.delete_a_namespace(setup_params["project2"]["name"])
            # Fail the test if we fall through. Delete operation should not have succeeded.
            pytest.fail("Expected Exception was not thrown! Namespace found.")
        except ocp_exceptions.OcpResourceNotFoundException:
            assert True

    def test_delete_labelled_projects(self, setup_params):
        """
        Positive path test for delete_labelled_projects.
        Validates that all the labelled projects are deleted.

        :param setup_params:
        :return:
        """
        #
        # Setup
        #
        project_api_obj = setup_params["project_api_obj"]
        project_api_obj.create_a_project(
            setup_params["project1"]["name"], labels_dict=setup_params["project1"]["label"]
        )
        project_api_obj.create_a_project(
            setup_params["project2"]["name"], labels_dict=setup_params["project2"]["label"]
        )

        #
        # Execution
        #
        try:
            project_api_obj.delete_labelled_projects(label_name="css-test=True")
            is_deleted_project1_present = project_api_obj.does_project_exist(setup_params["project1"]["name"])
            is_deleted_project2_present = project_api_obj.does_project_exist(setup_params["project2"]["name"])
            assert is_deleted_project1_present is False
            assert is_deleted_project2_present is False
        except ApiException as e:
            message = "Unexpected ApiException testing delete_labelled_projects!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])
            self.__cleanup(setup_params, setup_params["project2"]["name"])

    def test_get_labelled_projects(self, setup_params):
        """
        1. Get all labelled projects and determine the count.
        2. Create another project.
        3. Get all projects, determine the updated count and assert that it equals the original plus 1.
        4. Delete the created project, get all projects and assert that the original and final counts
           are equal.

        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
            api_response = project_api_obj.get_labelled_projects(label_selector="css-test=True")
            original_project_count = len(api_response.items)

            create_project_response = project_api_obj.create_a_project(
                setup_params["project1"]["name"], labels_dict=setup_params["project1"]["label"]
            )
            assert create_project_response.status.phase == "Active"

            updated_api_response = project_api_obj.get_labelled_projects(label_selector="css-test=True")
            updated_project_count = len(updated_api_response.items)
            assert updated_project_count == (original_project_count + 1)

            delete_project_response = project_api_obj.delete_a_project(setup_params["project1"]["name"])
            assert delete_project_response.status.phase == "Terminating"

            final_api_response = project_api_obj.get_labelled_projects(label_selector="css-test=True")
            final_project_count = len(final_api_response.items)
            assert final_project_count == original_project_count
        except ApiException as e:
            message = "Unexpected ApiException testing delete_labelled_projects!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

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
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        try:
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
        except ApiException as e:
            message = "Unexpected ApiException testing delete_labelled_projects!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])

    def test_does_project_exist(self, setup_params):
        """
        1. Create a project and validate that does_project_exist returns True.
        2. Delete the project and validate that does_project_exist returns False.
        :param setup_params:
        :return:
        """
        #
        # Execution
        #
        project_api_obj = setup_params["project_api_obj"]
        project_name = setup_params["project1"]["name"]
        project_label = setup_params["project1"]["label"]
        try:
            project_api_obj.create_a_project(project_name=project_name, labels_dict=project_label)
            is_created_project_present = project_api_obj.does_project_exist(project_name)
            assert is_created_project_present is True

            project_api_obj.delete_a_project(project_name=project_name)
            is_deleted_project_present = project_api_obj.does_project_exist(project_name)
            assert is_deleted_project_present is False
        except ApiException as e:
            message = "Unexpected ApiException testing delete_labelled_projects!"
            self.__log_exception_formatted(message, e)
            pytest.fail(message)

        #
        # Cleanup
        #
        finally:
            self.__cleanup(setup_params, setup_params["project1"]["name"])
