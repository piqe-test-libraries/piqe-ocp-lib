import logging
import pytest
from piqe_ocp_lib.api.resources.ocp_cluster_versions import OcpClusterVersion
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="session")
def ocp_cv(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpClusterVersion(kube_config_file=kube_config_file)


class TestOcpClusterVersion:

    def test_get_cluster_version(self, ocp_cv):
        """
        Verify that cluster version response is returned.
        :param ocp_cv: OcpClusterVersion class object
        :return:
        """
        logger.info("Get ClusterOperator operator detail")
        cluster_version_response = ocp_cv.get_cluster_version()
        logger.debug("Cluster Version Details : %s", cluster_version_response)
        if cluster_version_response:
            for cluster_version in cluster_version_response.items:
                if cluster_version["metadata"]["name"] != "version":
                    assert False, "Failed to get ClusterVersion operator details"

    def test_update_cluster_version(self, ocp_cv):
        """
        Verify that cluster version update response is returned and validate updated fields.
        :param ocp_cv: OcpClusterVersion class object
        :return:
        """
        logger.info("Update the ClusterVersion operator")
        cv_body = {
            "apiVersion": "config.openshift.io/v1",
            "kind": "ClusterVersion",
            "metadata": {
                "name": "version",
                "resourceVersion": "9589948",
            },
            "spec": {
                "channel": "fast-4.3",
                "clusterID": "38848dfd-09f4-4126-a92a-52d73863a028",
            },
        }
        updated_cluster_version_response = ocp_cv.update_cluster_version(cv_body=cv_body)

        if updated_cluster_version_response["metadata"]["name"] == cv_body["metadata"]["name"] and \
                updated_cluster_version_response["spec"]["channel"] == cv_body["spec"]["channel"]:
            assert True
        else:
            assert False, "Failed to update the ClusterVersion operator"

    def test_get_cluster_id(self, ocp_cv):
        """
        Verify that cluster ID is returned
        :param ocp_cv: OcpClusterVersion class object
        :return:
        """
        cluster_id = ocp_cv.get_cluster_id()
        assert isinstance(cluster_id, str)
