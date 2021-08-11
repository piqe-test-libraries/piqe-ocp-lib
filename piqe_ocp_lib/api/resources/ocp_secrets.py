import base64
import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpSecret(OcpBase):
    """
    OcpSecret Class extends OcpBase and encapsulates all methods
    related to managing Openshift secrets.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "v1"
        self.kind = "Secret"
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

        if api_response and api_response["metadata"]["name"] == secret_name:
            if api_response["type"] == "kubernetes.io/service-account-token":
                secret_token = api_response["data"]["token"]
            elif api_response["type"] == "Opaque":
                secret_token = api_response["data"]["saToken"]

        return secret_token

    def get_secret_names(self, namespace="default"):
        """
        Get secret names from specified namespace
        :param namespace: (string) name of namespace where secret exist
        :return: (list) List of secret names
        """
        api_response = None
        secret_name_list = list()
        try:
            api_response = self.ocp_secret.get(namespace=namespace)
        except ApiException as e:
            logger.exception("Exception while getting service account : %s\n" % e)

        if api_response:
            for secret in api_response.items:
                secret_name_list.append(secret["metadata"]["name"])

        return secret_name_list

    def get_long_live_bearer_token(self, sub_string="default-token", namespace="default"):
        """
        Get bearer token from secrets to authorize openshift cluster
        :param sub_string: (str) substring of secrets name to find actual secret name since openshift append random
        5 ascii digit at the end of every secret name
        :param namespace: (string) name of namespace where secret exist
        :return: (string) secret token for specified secret
        """
        secret_name_list = self.get_secret_names(namespace=namespace)
        try:
            secret_name = next(name for name in secret_name_list if sub_string in name)
        except StopIteration as e:
            logger.exception("Specified substring %s doesn't exist in %s namespace : %s", sub_string, namespace, e)

        bearer_token = self.get_secret_token(secret_name=secret_name, namespace=namespace)

        # All secret tokens in openshift are base64 encoded.
        # Decode base64 string into byte and convert byte to str
        if bearer_token:
            bearer_token = base64.b64decode(bearer_token).decode()

        return bearer_token

    def get_secret(self):
        pass

    def delete_secret(self, name):
        pass
