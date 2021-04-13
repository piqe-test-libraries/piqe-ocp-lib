import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpManagedCluster(OcpBase):
    """
    OcpManagedCluster Class extends OcpBase and encapsulates all methods
    related to Openshift ManagedCluster.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super(OcpManagedCluster, self).__init__(kube_config_file=kube_config_file)
        self.api_version = "cluster.open-cluster-management.io/v1"
        self.kind = "ManagedCluster"
        self.ocp_managed_cluster = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_managed_clusters(self, namespace="default"):
        """
        Get list of managed cluster by hub site
        :param namespace: (str) namespace
        :return: ManagedCluster api_response on success OR None on failure
        """
        api_response = None
        try:
            api_response = self.ocp_managed_cluster.get(namespace=namespace)
        except ApiException as e:
            logger.error("Exception while getting managed clusters : %s\n", e)

        return api_response

    def get_managed_cluster_names(self, namespace="default"):
        """
        Get managed cluster names
        :param namespace: namespace
        :return: list of names on success OR Empty list on failure
        """
        managed_clusters = list()
        managed_clustered_response = self.get_managed_clusters(namespace=namespace)

        if managed_clustered_response:
            for item in managed_clustered_response.items:
                managed_clusters.append(item.metadata.name)
        else:
            logger.exception("Managed cluster response is None or there are no managed cluster in hub site")

        return managed_clusters

    def is_managed_cluster_self_registered(self, name, namespace="default"):
        """
        Check if managed cluster is self registered in to ACM running on hub site
        :param name: (str) name of managed cluster
        :param namespace: namespace
        :return: Tuple of boolean and dict on success
        """
        is_managed_cluster_joined = False
        managed_clustered_status = dict()
        managed_clustered_response = self.get_managed_clusters(namespace=namespace)

        if managed_clustered_response:
            for item in managed_clustered_response.items:
                if item.metadata.name == name:
                    for condition in item.status.conditions:
                        if condition["type"] == "HubAcceptedManagedCluster":
                            managed_clustered_status["HubAcceptedManagedCluster"] = condition["status"]
                        elif condition["type"] == "ManagedClusterConditionAvailable":
                            managed_clustered_status["ManagedClusterConditionAvailable"] = condition["status"]
                        elif condition["type"] == "ManagedClusterJoined":
                            is_managed_cluster_joined = True
                            managed_clustered_status["ManagedClusterJoined"] = condition["status"]
        else:
            logger.exception("Managed cluster response is None or there are no managed cluster in hub site")

        return is_managed_cluster_joined, managed_clustered_status
