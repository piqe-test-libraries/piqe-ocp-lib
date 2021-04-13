import logging
import pytest
from piqe_ocp_lib.api.resources.ocp_configs import OcpConfig
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)

# Note : This unittest will use image registry config. if you want to run against any other config,
# Please change the API_VERSION
KIND = "Config"
API_VERSION = "imageregistry.operator.openshift.io/v1"
pytest.config_response = None
pytest.config_response_before_update = None


@pytest.fixture(scope="session")
def ocp_config(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpConfig(kind=KIND, api_version=API_VERSION, kube_config_file=kube_config_file)


class TestOcpConfig:
    def test_get_all_ocp_config(self, ocp_config):
        """
        Verify that openshift config response for all resources in specified api version is returned
        :param ocp_config: OcpConfig class object
        :return:
        """
        logger.info("Get openshift configs for %s api version", API_VERSION)
        pytest.config_response = ocp_config.get_all_ocp_config()
        logger.debug("Config Response : %s", pytest.config_response)
        if not pytest.config_response and len(pytest.config_response.items) <= 0:
            assert False, f"Failed to get config for {API_VERSION} api version"

    def test_get_ocp_config(self, ocp_config):
        """
        Verify that openshift config response for specified resource of that api version is returned
        :param ocp_config: OcpConfig class object
        :return:
        """
        for config in pytest.config_response.items:
            name = config["metadata"]["name"]
            break
        config_response = ocp_config.get_ocp_config(name=name)
        logger.debug("Config Response : %s", config_response)
        if not config_response and config_response["metadata"]["name"] != name:
            assert False, f"Failed to get config for {name}"

    def test_update_ocp_config(self, ocp_config):
        """
        Verify that updated config response for specified resource of that api version is returned
        :param ocp_config: OcpConfig class object
        :return:
        """
        for config in pytest.config_response.items:
            name = config["metadata"]["name"]
            pytest.config_response_before_update = config
            break
        logger.info(f"Update the openshift config for {name}")
        logger.debug("Config before update : %s", pytest.config_response_before_update)

        # Update the config body based on specific api version config
        # Following body is for image registry config
        config_body = {
            "apiVersion": API_VERSION,
            "kind": KIND,
            "metadata": {
                "name": name,
                "resourceVersion": "10287401",
            },
            "spec": {"managementState": "Removed", "replicas": 1, "logging": 2, "storage": {"emptyDir": {}}},
        }

        config_response_after_update = ocp_config.update_ocp_config(config_body=config_body)
        logger.debug("Config Response after update : %s", config_response_after_update)

        if not config_response_after_update:
            assert False, "Failed to update openshift config"
