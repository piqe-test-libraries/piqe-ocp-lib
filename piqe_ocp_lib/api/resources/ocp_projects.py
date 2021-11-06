import logging
from typing import Optional

from openshift.dynamic.resource import ResourceInstance

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api import ocp_exceptions
from piqe_ocp_lib.api.ocp_exception_handler import handle_exception

from .ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpProjects(OcpBase):
    """
    OcpProjects Class extends OcpBase and encapsulates all methods
    related to managing Openshift projects.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file: Optional[str] = None):
        """
        The init method for the OcpProjects class
        :return: None
        """
        self.kube_config_file = kube_config_file
        OcpBase.__init__(self, kube_config_file=self.kube_config_file)
        self.api_version = "v1"
        self.ocp_projects = self.dyn_client.resources.get(api_version=self.api_version, kind="Namespace")
        self.create_ocp_projects = self.dyn_client.resources.get(api_version=self.api_version, kind="ProjectRequest")

    @handle_exception
    def create_a_project(self, project_name: str, labels_dict: Optional[dict] = None) -> Optional[ResourceInstance]:
        """
        Method to create a project
        :param project_name: (required | str) Name of project to be created.
        :param labels_dict: (optional | dict) a dictionary of key/val label pairs.
        :return: A V1ProjectRequest object on success. None on failure
        """
        api_response = self.create_ocp_projects.create(body={"metadata": {"name": project_name}})
        if self._watch_is_project_created(project_name) is False:
            logger.error("Failed to create the project: %s\n", project_name)
            return None
        if labels_dict is not None:
            self.label_a_project(project_name, labels_dict)
        return api_response

    @handle_exception
    def create_a_namespace(self, namespace_name: str, labels_dict: Optional[dict] = None) -> Optional[ResourceInstance]:
        """
        Method to create a project/namespace with "openshift" in the beginning of the name.
        :param namespace_name: (required | str) Name of project to be created.
        :param labels_dict: (optional | dict) a dictionary of key/val label pairs.
        :return: A V1ProjectRequest object on success. None on failure
        """
        api_response = self.ocp_projects.create(body={"metadata": {"name": namespace_name}})
        if self._watch_is_project_created(namespace_name) is False:
            logger.error("Failed to create the namespace: %s\n", namespace_name)
            return None
        if labels_dict is not None:
            self.label_a_project(namespace_name, labels_dict)
        return api_response

    @handle_exception
    def label_a_project(self, project_name: str, labels_dict: dict) -> Optional[ResourceInstance]:
        """
        Method that patches a project with user
        defined labels
        :param project_name: (required | str) Name of the project to be patched.
        :param labels_dict: (required | dict) An object of type dict(str: str)
        :return: An object of type V1Namespace
        """
        body = {"metadata": {"labels": labels_dict}}
        api_response = self.ocp_projects.patch(body=body, name=project_name)
        return api_response

    @handle_exception
    def get_a_project(self, project_name: str) -> Optional[ResourceInstance]:
        """
        Method that returns a project by name.
        :param project_name: (required | str) Name of the project to be patched.
        :return: An object of type V1Namespace
        """
        api_response = self.ocp_projects.get(name=project_name)
        return api_response

    @handle_exception
    def delete_a_project(self, project_name: str) -> Optional[ResourceInstance]:
        """
        Method that deletes a project by name.
        :param project_name: (required | str) Name of the project to be deleted.
        :return: An object of type V1Namespace
        """
        api_response = self.ocp_projects.delete(name=project_name)
        if self._watch_is_project_deleted(project_name) is False:
            return None
        return api_response

    @handle_exception
    def delete_a_namespace(self, namespace_name: str) -> Optional[ResourceInstance]:
        """
        Method that deletes a project by name.
        :param namespace_name: (required | str) Name of the namespace to be deleted.
        :return: An object of type V1Namespace
        """
        api_response = self.ocp_projects.delete(name=namespace_name)
        if self._watch_is_project_deleted(namespace_name) is False:
            return None
        return api_response

    @handle_exception
    def delete_labelled_projects(self, label_name: str) -> list:
        """
        Method that deletes all projects with the specified label.
        :param label_name: (required | str) label of the projects to be deleted.
        :return: A list containing objects of type V1Namespace
        """
        deleted_projects = []
        labelled_projects = self.get_labelled_projects(label_selector=label_name)
        for project in labelled_projects.items:
            api_response = self.ocp_projects.delete(name=project.metadata.name)
            if self._watch_is_project_deleted(project.metadata.name):
                deleted_projects.append(api_response)
        return deleted_projects

    @handle_exception
    def get_labelled_projects(self, label_selector: str) -> Optional[ResourceInstance]:
        """
        Method that returns all projects with a label selector.
        :param label_selector: (required | str) label for the projects to be fetched.
        :return: An object of type V1NamespaceList
        """
        api_response = self.ocp_projects.get(label_selector=label_selector)
        return api_response

    @handle_exception
    def get_all_projects(self) -> Optional[ResourceInstance]:
        """
        Method that returns all projects in a cluster.
        :param : None
        :return: An object of type V1NamespaceList
        """
        api_response = self.ocp_projects.get()
        return api_response

    def does_project_exist(self, project_name: str) -> bool:
        """
        Determine if the specified project exists.
        :param project_name: (required | str) Name of project to be checked.
        :return: True if the project is found. False if the project is not found.
        """
        try:
            has_project = self.get_a_project(project_name)
        except ocp_exceptions.OcpResourceNotFoundException:
            return False
        return bool(has_project)

    def _watch_is_project_created(self, project_name: str) -> bool:
        """
        Provide a watch mechanism to follow project create operations.

        :param: project_name: (required | str) Name of project to be checked.
        :return: True if the project is Created, False if the project is not found or the
                 state cannot be determined.
        """
        field_selector = "status.phase=Active"
        for event in self.ocp_projects.watch(namespace=project_name, field_selector=field_selector, timeout=600):
            logger.info("Project : {}, Creation phase : {}".format(project_name, event["object"]["status"]["phase"]))
            if self.does_project_exist(project_name):
                return True
        return False

    def _watch_is_project_deleted(self, project_name: str) -> bool:
        """
        Provide a watch mechanism to follow project delete operations.

        :param: project_name: (required | str) Name of project to be checked.
        :return: True if the project has been deleted, False if the project is not found.
        """
        field_selector = "status.phase=Terminating"
        for event in self.ocp_projects.watch(namespace=project_name, field_selector=field_selector, timeout=600):
            logger.info("Project : {}, Deletion phase : {}".format(project_name, event["object"]["status"]["phase"]))
            if not self.does_project_exist(project_name):
                return True
        return False
