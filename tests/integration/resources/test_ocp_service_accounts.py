import logging
import pytest
from piqe_ocp_lib.api.resources.ocp_service_accounts import OcpServiceAccount
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)

SERVICE_ACCOUNT_NAME = "default"


@pytest.fixture(scope="session")
def ocp_service_account(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpServiceAccount(kube_config_file=kube_config_file)


class TestOcpServiceAccounts:

    def test_get_list_of_service_account_secret_names(self, ocp_service_account):
        list_of_secrets = ocp_service_account.get_list_of_service_account_secret_names(
            name=SERVICE_ACCOUNT_NAME, namespace="default"
        )
        logger.info("List of secrets in %s is %s", SERVICE_ACCOUNT_NAME, list_of_secrets)
        if not len(list_of_secrets) > 0:
            assert False

    def test_create_service_account(self):
        pass

    def test_delete_service_account(self):
        pass
