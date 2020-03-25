import logging
from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpServiceAccount(OcpBase):
    """
    OcpServiceAccount Class extends OcpBase and encapsulates all methods
    related to managing Openshift ServiceAccount.
    :param kube_config_file: A kubernetes config file. It overrides
                             the hostname/username/password params
                             if specified.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(OcpServiceAccount, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'v1'
        self.kind = 'ServiceAccount'
        self.ocp_service_account = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_list_of_service_account_secret_names(self, name, namespace):
        """
        Get service account secrets
        :param name: (string) Name of Service Account
        :param namespace: (string) Name of namespace where service account was created
        :return: (list) list of service account secret names
        """
        api_response = None
        list_of_secret_names = list()
        try:
            api_response = self.ocp_service_account.get(name=name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception while getting service account : %s\n" % e)

        if api_response:
            for secret in api_response["secrets"]:
                list_of_secret_names.append(secret["name"])

        return list_of_secret_names

    def create_service_account(self):
        pass

    def delete_service_account(self):
        pass
