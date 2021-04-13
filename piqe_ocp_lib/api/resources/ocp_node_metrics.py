import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpNodeMetrics(OcpBase):
    """
    OcpNodeMetrics Class extends OcpBase and encapsulates all methods
    related to managing Openshift nodes Metrics.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super(OcpNodeMetrics, self).__init__(kube_config_file=kube_config_file)
        self.api_version = "metrics.k8s.io/v1beta1"
        self.kind = "NodeMetrics"
        self.ocp_nodes = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_node_metrics(self, node_name):
        """
        Method returns a node metrics by name for specific node

        :param node_name: The name of the node.
        :return: node_metric_response (ResourceInstance) on success OR None on failure.
        """
        node_metric_response = None
        try:
            node_metric_response = self.ocp_nodes.get(name=node_name)
        except ApiException as e:
            logger.error("Exception encountered while getting node metrics by name: %s\n", e)
        logger.debug("Node metric response : %s", node_metric_response)
        return node_metric_response

    def get_nodes_metrics(self):
        """
        Method returns a node metrics for all nodes

        :return: node_metric_response on success. None on failure.
        """
        node_metric_response = None
        try:
            node_metric_response = self.ocp_nodes.get()
        except ApiException as e:
            logger.error("Exception encountered while getting node metrics: %s\n", e)
        logger.debug("Node metric response : %s", node_metric_response)
        return node_metric_response
