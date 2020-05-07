from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from kubernetes.client.rest import ApiException
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpClusterVersion(OcpBase):
    """
    OcpClusterVersion class extends OcpBase and encapsulates all methods
    related to managing Openshift Cluster Version.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super(OcpClusterVersion, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'config.openshift.io/v1'
        self.kind = 'ClusterVersion'
        self.ocp_cv = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_cluster_version(self):
        """
        Get ClusterVersion operator details
        :return: (list) ClusterVersion API response on success OR None on Failure
        """
        cluster_version_response = None
        try:
            cluster_version_response = self.ocp_cv.get()
        except ApiException as e:
            logger.error("Exception while getting cluster version %s : %s\n", e)

        return cluster_version_response

    def update_cluster_version(self, cv_body):
        """
        Update ClusterVersion operator
        :param cv_body: (dict) Updated body of ClusterVersion operator
        :return: (Dict) ClusterVersion API response on success OR None on Failure
        """
        update_cluster_version_response = None
        if cv_body:

            # Add/Update resourceVersion under metadata and clusterID under spec to match of existing resource.These two
            # field are also required to properly update ClusterVersion operator. Without these two fields,API call will
            # succeed but changes won't be applied.
            actual_cluster_version_response = self.get_cluster_version()
            for cluster_version in actual_cluster_version_response.items:
                if cluster_version["metadata"]["name"] == "version":
                    cv_body["metadata"]["resourceVersion"] = cluster_version["metadata"]["resourceVersion"]
                    cv_body["spec"]["clusterID"] = cluster_version["spec"]["clusterID"]

            try:
                update_cluster_version_response = self.ocp_cv.replace(body=cv_body)
            except ApiException as e:
                logger.exception("Exception while updating cluster version : %s\n" % e)
        else:
            logger.error("Cluster version body is empty. Please provide config body with field to be updated")

        return update_cluster_version_response

    def get_cluster_id(self):
        """
        Get cluster ID
        :return: (str) cluster_id on success or None on failure
        """
        cluster_id = None
        cluster_version_response = self.get_cluster_version()
        for item in cluster_version_response.items:
            if item["metadata"]["name"] == "version" and "clusterID" in dict(item["spec"]):
                cluster_id = item["spec"]["clusterID"]
        logger.info("Cluster ID : %s", cluster_id)

        return cluster_id
