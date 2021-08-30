import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpConfigMaps(OcpBase):
    """
    OcpConfigMaps Class extends OcpBase and encapsulates all methods
    related to openshift config maps.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "v1"
        self.kind = "ConfigMap"
        self.ocp_config_map = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_config_map(self, config_maps_body):
        """
        Create a ConfigMaps in specific namespace
        :param config_maps_body (dict) ConfigMaps definitions
        :return: CreateConfigMaps response on success OR None on Failure
        """
        create_cm_response = None
        try:
            create_cm_response = self.ocp_config_map.create(body=config_maps_body)
        except ApiException as e:
            logger.exception(f"Exception while creating ConfigMaps definitions : {e}\n")

        return create_cm_response

    def get_config_maps(self, namespace):
        """
        Get all ConfigMaps from specific namespace
        :param namespace: (str) name of the namespace
        :return: ConfigMaps response on Success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_config_map.get(namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting ConfigMaps : {e}\n")

        return api_response

    def get_config_maps_names(self, namespace):
        """
        Get names of all ConfigMaps from specific namespace
        :param namespace: (str) name of the namespace
        :return: List of ConfigMaps names on Success OR Empty list on Failure
        """
        list_of_cm_names = list()
        cm_response = self.get_config_maps(namespace=namespace)

        if cm_response:
            for cm in cm_response.items:
                list_of_cm_names.append(cm.metadata.name)
        else:
            logger.warning(f"There are no ConfigMaps in {namespace} namespace")

        return list_of_cm_names

    def get_a_config_map(self, name, namespace):
        """
        Get a specific ConfigMaps from specific namespace
        :param name: (str) name of ConfigMaps
        :param namespace: (str) namespace where ConfigMaps is created
        :return: ConfigMaps response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_config_map.get(name=name, namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting a {name} ConfigMaps : {e}\n")

        return api_response

    def delete_a_config_map(self, name, namespace):
        """
        Delete a specified ConfigMap from specified namespace
        :param name: (str) name of ConfigMaps
        :param namespace: (str) name of namespace where ConfigMaps was created
        :return: Delete response on success OR None on Failure

        ResourceInstance[Status]:
          apiVersion: v1
          details:
            kind: configmaps
            name: test
            uid: aa1a8359-42b0-45f9-b44b-cd0ecbff6ef8
          kind: Status
          metadata: {}
          status: Success

        """
        api_response = None
        try:
            api_response = self.ocp_config_map.delete(name, namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting {name} ConfigMaps: {e}\n")
        return api_response
