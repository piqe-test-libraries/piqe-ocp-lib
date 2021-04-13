import logging
import random

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_config_maps import OcpConfigMaps

logger = logging.getLogger(__loggername__)

five_digit_number = "".join(random.sample("0123456789", 5))
NAMESPACE = "default"
NAME = f"test{five_digit_number}"


@pytest.fixture(scope="session")
def ocp_cm(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpConfigMaps(kube_config_file=kube_config_file)


class TestOcpConfigMaps:
    def test_create_config_map(self, ocp_cm):
        logger.info(f"Create a {NAME} ConfigMaps in {NAMESPACE} namespace")
        cm_body = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": NAME,
                "namespace": NAMESPACE,
            },
            "data": {"name": "css-qe", "group": "CSS"},
        }
        create_cm_response = ocp_cm.create_config_map(config_maps_body=cm_body)
        logger.info(f"Create Response : {create_cm_response}")
        # logger.info("Wait for 10 secs to create ConfigMaps")
        # time.sleep(10)
        if not create_cm_response.metadata.name == NAME and not create_cm_response.metadata.namespace == NAMESPACE:
            assert False, f"Failed to create {NAME} ConfigMpas in {NAMESPACE} namespace"

    def test_get_config_maps(self, ocp_cm):
        logger.info("Get config maps")
        cm_response = ocp_cm.get_config_maps(namespace=NAMESPACE)
        if not cm_response and len(cm_response.items) <= 0:
            assert False, "Failed to get ConfigMaps"

    def test_get_a_config_map(self, ocp_cm):
        logger.info(f"Get a {NAME} config map")
        a_cm_response = ocp_cm.get_config_maps(namespace=NAMESPACE)
        if not a_cm_response and len(a_cm_response.items) <= 0:
            assert False, f"Failed to get {NAME} ConfigMaps"

    def test_get_config_maps_names(self, ocp_cm):
        logger.info("Get all config maps from specified namespace")
        cm_names = ocp_cm.get_config_maps_names(namespace=NAMESPACE)
        if not cm_names and len(cm_names.items) <= 0:
            assert False, f"Failed to get ConfigMaps in {NAMESPACE} namespace"

    def test_delete_a_config_map(self, ocp_cm):
        logger.info(f"Delete a {NAME} ConfigMap")
        delete_cm_response = ocp_cm.delete_a_config_map(name=NAME, namespace=NAMESPACE)
        logger.info(f"Delete Response : {delete_cm_response}")
        if not delete_cm_response and delete_cm_response["status"] != "Success":
            assert False, f"Failed to delete {NAME} ConfigMaps in {NAMESPACE} namespace"
