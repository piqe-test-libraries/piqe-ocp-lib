import logging
import pytest
import random
from piqe_ocp_lib.api.resources.ocp_cluster_operators import OcpClusterOperator
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)

pytest.operator_names = None


@pytest.fixture(scope="session")
def ocp_co(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpClusterOperator(kube_config_file=kube_config_file)


class TestOcpClusterOperator:
    def test_get_cluster_operators_name(self, ocp_co):
        """
        Verify that list of cluster operators names are returned
        :param ocp_co: OcpClusterOperator class object
        :return:
        """
        logger.info("Get cluster operators name ONLY")
        pytest.operator_names = ocp_co.get_cluster_operators_name()
        logger.debug("Cluster Operator Names : %s", pytest.operator_names)

        if len(pytest.operator_names) == 0:
            assert False, "Failed to get cluster operators name OR there are no cluster operator"

    def test_get_cluster_operator(self, ocp_co):
        """
        Verify that specific cluster operator response is returned
        :param ocp_co: OcpClusterOperator class object
        :return:
        """
        cluster_operator_name = random.choice(pytest.operator_names)
        logger.info("Get %s cluster operator", cluster_operator_name)
        cluster_operator_response = ocp_co.get_cluster_operator(name=cluster_operator_name)
        logger.debug("%s cluster operator response : %s\n", cluster_operator_name, cluster_operator_response)

        if not cluster_operator_response["metadata"]["name"] == cluster_operator_name:
            assert False, f"Failed to get {cluster_operator_name} cluster operator"

    def test_get_all_cluster_operators(self, ocp_co):
        """
        Verify that cluster operator response for all operators are returned
        :param ocp_co: OcpClusterOperator class object
        :return:
        """
        logger.info("Get all cluster operators")
        cluster_operator_response = ocp_co.get_all_cluster_operators()
        logger.debug("All cluster operator response : %s\n", cluster_operator_response)

        if len(cluster_operator_response.items) == 0:
            assert False, "Failed to get cluster operator OR there are no cluster operator"
