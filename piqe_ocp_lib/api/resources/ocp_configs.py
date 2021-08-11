import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpConfig(OcpBase):
    """
    OcpConfig Class extends OcpBase and encapsulates all methods
    related to managing Openshift Config related operations.
    :param kind: (str) kubernetes/openshift resource kind/type
    :param api_version: (str) kubernetes/openshift api version
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kind, api_version, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.kube_config_file = kube_config_file
        self.ocp_config = self.dyn_client.resources.get(api_version=api_version, kind=kind)

    def get_ocp_config(self, name):
        """
        Get openshift config for specified resource name
        :param name: (str) openshift config resource name
        :return: (bool) Return API response on success otherwise None
        """
        logger.info("Get openshift config for %s", name)
        config_response = None
        try:
            config_response = self.ocp_config.get(name=name)
        except ApiException as e:
            logger.error("Exception while getting ocp config: %s\n", e)

        return config_response

    def get_all_ocp_config(self):
        """
        Get openshift config for all resources
        :return: (bool) Return API response on success otherwise None
        """
        logger.info("Get all openshift config")
        config_response = None
        try:
            config_response = self.ocp_config.get()
        except ApiException as e:
            logger.error("Exception while getting ocp config: %s\n", e)

        return config_response

    def update_ocp_config(self, config_body):
        """
        Update openshift config resource
        :param config_body: (dict) body of openshift config resource
        :return: (bool) Return API response on success otherwise None
        """
        config_response = None
        if config_body:
            name = config_body["metadata"]["name"]
            api_version = config_body["apiVersion"]
            logger.info("Update openshift config for %s and apiVersion %s", name, api_version)

            # Before updating any openshift config, resourceVersion should match with existing config.
            # logging (loglevel) and replicas are required fields update openshift config.
            # OtherwiseAPI call will fail.
            original_config_response = self.get_ocp_config(name=name)
            config_body["metadata"]["resourceVersion"] = original_config_response["metadata"]["resourceVersion"]
            config_body["spec"]["replicas"] = original_config_response["spec"]["replicas"]
            config_body["spec"]["logging"] = original_config_response["spec"]["logging"]

            try:
                config_response = self.ocp_config.replace(body=config_body)
            except ApiException as e:
                logger.error("Exception while updating ocp config: %s\n", e)
        else:
            logger.error("config body is empty. Please provide config body with field to be updated")

        return config_response
