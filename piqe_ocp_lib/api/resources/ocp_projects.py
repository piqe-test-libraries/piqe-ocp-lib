import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__

from .ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpProjects(OcpBase):
    """
    OcpProjects Class extends OcpBase and encapsulates all methods
    related to managing Openshift projects.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        self.kube_config_file = kube_config_file
        OcpBase.__init__(self, kube_config_file=self.kube_config_file)
        self.api_version = "v1"
        self.ocp_projects = self.dyn_client.resources.get(api_version=self.api_version, kind="Namespace")
        self.create_ocp_projects = self.dyn_client.resources.get(api_version=self.api_version, kind="ProjectRequest")

    def create_a_project(self, project_name, labels_dict=None):
        """
        Method to create a project
        :param project_name: (required | str) Name of project to be created.
        :param labels_dict: (optional | dict) a dictionary of key/val label pairs.
        :return: A V1ProjectRequest object on success. None on failure
        """
        api_response = None
        try:
            api_response = self.create_ocp_projects.create(body={"metadata": {"name": project_name}})
            if self._watch_is_project_created(project_name) is False:
                return None
        except ApiException as e:
            logger.error("Exception when calling method create_project_request: %s\n" % e)
        if labels_dict is not None:
            self.label_a_project(project_name, labels_dict)
        return api_response

    def create_a_namespace(self, namespace_name, labels_dict=None):
        """
        Method to create a project/namespace with "openshift" in the beginning of the name.
        :param namespace_name: (required | str) Name of project to be created.
        :param labels_dict: (optional | dict) a dictionary of key/val label pairs.
        :return: A V1ProjectRequest object on success. None on failure
        """
        api_response = None
        try:
            api_response = self.ocp_projects.create(body={"metadata": {"name": namespace_name}})
            if self._watch_is_project_created(namespace_name) is False:
                return None
        except ApiException as e:
            logger.error("Exception when calling method create_project_request: %s\n" % e)
        if labels_dict is not None:
            self.label_a_project(namespace_name, labels_dict)
        return api_response

    def label_a_project(self, project_name, labels_dict):
        """
        Method that patches a project with user
        defined labels
        :param project_name: (required | str) Name of the project to be patched.
        :param labels_dict: (required | dict) An object of type dict(str: str)
        :return: An object of type V1Namespace
        """
        api_response = None
        body = {"metadata": {"labels": labels_dict}}
        try:
            api_response = self.ocp_projects.patch(body=body, name=project_name)
        except ApiException as e:
            logger.error("Exception when calling method patch_namespace: %s\n" % e)
        return api_response

    def get_a_project(self, project_name):
        """
        Method that returns a project by name.
        :param project_name: (required | str) Name of the project to be patched.
        :return: An object of type V1Namespace
        """
        api_response = None
        try:
            api_response = self.ocp_projects.get(name=project_name)
        except ApiException as e:
            logger.error("Exception when calling method get_a_project: %s\n" % e)
        return api_response

    def delete_a_project(self, project_name):
        """
        Method that deletes a project by name.
        :param project_name: (required | str) Name of the project to be deleted.
        :return: An object of type V1Namespace
        """
        api_response = None
        try:
            api_response = self.ocp_projects.delete(name=project_name)
            if self._watch_is_project_deleted(project_name) is False:
                return None
        except ApiException as e:
            logger.error("Exception when calling method delete_a_project: %s\n" % e)
        return api_response

    def delete_a_namespace(self, namespace_name):
        """
        Method that deletes a project by name.
        :param namespace_name: (required | str) Name of the namespace to be deleted.
        :return: An object of type V1Namespace
        """
        api_response = None
        try:
            api_response = self.ocp_projects.delete(name=namespace_name)
            if self._watch_is_project_deleted(namespace_name) is False:
                return None
        except ApiException as e:
            logger.error("Exception when calling method delete_a_namespace: %s\n" % e)
        return api_response

    def get_all_projects(self):
        """
        Method that returns all projects in a cluster.
        :param : None
        :return: An object of type V1NamespaceList
        """
        api_response = None
        try:
            api_response = self.ocp_projects.get()
        except ApiException as e:
            logger.error("Exception when calling method list_all_namespaces: %s\n" % e)
        return api_response

    def does_project_exist(self, project_name):
        """
        Determine if the specified project exists.
        :param project_name:
        :return: True if the project is found. False if the project is not found.
        """
        has_project = self.get_a_project(project_name)
        return bool(has_project)

    def _watch_is_project_created(self, project_name):
        """
        Provide a watch mechanism to follow project create operations.

        :param: project_name:
        :param: timeout: The timeout (in seconds) passed to the watch().
        :return: True if the project is Created, False if the project is not found or the
                 state cannot be determined.
        """
        field_selector = "status.phase=Active"
        for event in self.ocp_projects.watch(namespace=project_name, field_selector=field_selector, timeout=600):
            logger.info("Project : {}, Creation phase : {}".format(project_name, event["object"]["status"]["phase"]))
            if self.does_project_exist(project_name):
                return True
        return False

    def _watch_is_project_deleted(self, project_name):
        """
        Provide a watch mechanism to follow project delete operations.

        :param: project_name:
        :param: timeout: The timeout (in seconds) passed to the watch().
        :return: True if the project has been deleted, False if the project is not found.
        """
        field_selector = "status.phase=Terminating"
        for event in self.ocp_projects.watch(namespace=project_name, field_selector=field_selector, timeout=600):
            logger.info("Project : {}, Deletion phase : {}".format(project_name, event["object"]["status"]["phase"]))
            if not self.does_project_exist(project_name):
                return True
        return False
