import logging
from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpSecret(OcpBase):
    """
    OcpSecret Class extends OcpBase and encapsulates all methods
    related to managing Openshift secrets.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(OcpSecret, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'v1'
        self.kind = 'Secret'
        self.ocp_secret = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_secret(self, secret_cred_body):
        """
        Create secret credentials
        :param secret_cred_body : (string) Migration storage credential body
        :return: return api_response
        """
        logger.debug("Secret Credential Body : %s", secret_cred_body)
        api_response = None
        try:
            api_response = self.ocp_secret.create(body=secret_cred_body)
        except ApiException as e:
            logger.exception("Exception while creating secret cred: %s\n" % e)
        logger.info("Secret credentials response : %s", api_response)
        return api_response

    def get_secret_token(self, secret_name, namespace="default"):
        """
        Get service account secret token from openshift cluster
        :param secret_name: (string) secret name for which we want to get secret token
        :param namespace: (string) name of namespace where secret exist
        :return: (string) secret token for specified secret
        """
        secret_token = None
        api_response = None
        try:
            api_response = self.ocp_secret.get(name=secret_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception while getting service account : %s\n" % e)

        logger.info("Secret Response = %s", api_response)

        if api_response and api_response["metadata"]["name"] == secret_name:
            if api_response["type"] == "kubernetes.io/service-account-token":
                secret_token = api_response["data"]["token"]
            elif api_response["type"] == "Opaque":
                secret_token = api_response["data"]["saToken"]

        return secret_token

    def get_secret(self):
        pass

    def delete_secret(self, name):
        pass
