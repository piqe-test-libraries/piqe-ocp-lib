import logging
import pytest
import random
from piqe_ocp_lib.api.resources.ocp_nodes import OcpNodes
from piqe_ocp_lib.api.resources.ocp_node_metrics import OcpNodeMetrics
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope='class')
def ocp_node_metric(get_kubeconfig):
    return OcpNodeMetrics(kube_config_file=get_kubeconfig)


@pytest.fixture(scope='class')
def ocp_node(get_kubeconfig):
    return OcpNodes(kube_config_file=get_kubeconfig)


@pytest.mark.skip(reason="Skip until CSS-3341 is resolved")
class TestOcpNodeMetrics:

    def test_get_a_node_metrics(self, ocp_node_metric, ocp_node):
        """
        Verify that node metric resource instance is created and returned a
        response for specific node with node metrics
        :param ocp_node_metric: Instance of OcpNodeMetrics class
        :param ocp_node: Instance of OcpNode class
        :return: None
        """
        logger.info("Get available nodes from cluster and pick one randomly")
        node_list = ocp_node.get_all_node_names()
        node_name = random.choice(node_list)
        logger.info("Get node metrics for specific node")
        metric_response = ocp_node_metric.get_node_metrics(node_name=node_name)
        assert metric_response.kind == "NodeMetrics"
        if not metric_response:
            assert False, f"Failed to get node metrics for node {node_name}"

    def test_get_node_metrics(self, ocp_node_metric):
        """
        Verify that node metric resource instance is created and returned a list of
        response for ALL nodes with node metrics
        :param ocp_node_metric: Instance of OcpNodeMetrics class
        :return: None
        """
        logger.info("Get node metrics for all nodes")
        metric_response = ocp_node_metric.get_nodes_metrics()
        assert metric_response.kind == "NodeMetricsList"
        if not metric_response:
            assert False, "Failed to get nodes metrics"
