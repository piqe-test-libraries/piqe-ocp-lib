import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpClusterOperator(OcpBase):
    """
    OcpClusterOperator class extends OcpBase and encapsulates all methods
    related to managing Openshift Cluster Operator.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "config.openshift.io/v1"
        self.kind = "ClusterOperator"
        self.ocp_co = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_cluster_operator(self, name):
        """
        Get specific cluster operator
        :param name: (str) Name of the cluster operator i.e. authentication
        :return: (Dict) API Response on success or None on Failure
        """
        cluster_operator = None
        try:
            cluster_operator = self.ocp_co.get(name=name)
        except ApiException as e:
            logger.error("Exception while getting cluster operator %s : %s\n", name, e)

        return cluster_operator

    def get_all_cluster_operators(self):
        """
        Get all cluster operators from openshift cluster
        :return: (Dict) API Response on success or None on Failure
        """
        cluster_operators = None
        try:
            cluster_operators = self.ocp_co.get()
        except ApiException as e:
            logger.error("Exception while getting cluster operators: %s\n", e)

        return cluster_operators

    def get_cluster_operators_name(self):
        """
        Get cluster operators name
        :return: (list) Return list of cluster operator names only
        """
        cluster_operators_name = list()
        try:
            cluster_operators = self.ocp_co.get()
        except ApiException as e:
            logger.error("Exception while getting cluster operators: %s\n", e)

        if cluster_operators:
            for cluster_operator in cluster_operators.items:
                cluster_operators_name.append(cluster_operator["metadata"]["name"])

        return cluster_operators_name
