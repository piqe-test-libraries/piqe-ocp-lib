import logging
import pytest
from piqe_ocp_lib.api.resources.ocp_health_checker import OcpHealthChecker
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="session")
def ocp_health(get_kubeconfig):
    return OcpHealthChecker(kube_config_file=get_kubeconfig)


class TestOcpHealthChecker:
    def test_check_node_health(self, ocp_health):
        """
        Verify the node health status (bool) and failure nodes (dict) if any are returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of openshift nodes")
        all_nodes_healthy, node_health_info = ocp_health.check_node_health()
        assert isinstance(all_nodes_healthy, bool)
        assert isinstance(node_health_info, dict)
        # if all_nodes_healthy is False, There has to be values of failure nodes in node_health_info dict
        if all_nodes_healthy:
            for key, value in node_health_info.items():
                assert len(value) == 0
        else:
            failure_values = list()
            for key, value in node_health_info.items():
                failure_values.append(value)
            assert len(failure_values) > 0

    def test_check_router_health(self, ocp_health):
        """
        Verify the openshift router health status (bool) and failure (dict) are returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of openshift router")
        is_router_healthy, unhealthy_router_info = ocp_health.check_router_health()
        assert isinstance(is_router_healthy, bool)
        assert isinstance(unhealthy_router_info, dict)
        if not is_router_healthy:
            for key, value in unhealthy_router_info.items():
                assert len(value) > 0

    def test_check_image_registry_health(self, ocp_health):
        """
        Verify the openshift image registry health status (bool) and failure components (dict) are returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of openshift image registry")
        is_image_registry_healthy, unhealthy_image_registry_info = ocp_health.check_image_registry_health()
        assert isinstance(is_image_registry_healthy, bool)
        assert isinstance(unhealthy_image_registry_info, dict)
        if not is_image_registry_healthy:
            for key, value in unhealthy_image_registry_info.items():
                assert len(value) > 0

    def test_check_persistence_storage_for_image_registry(self, ocp_health):
        """
         Verify the status of persistence storage for image registry (bool) is returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check persistence storage for image registry")
        is_image_registry_storage_configured = ocp_health.check_persistence_storage_for_image_registry()
        assert isinstance(is_image_registry_storage_configured, bool)

    def test_check_api_server_health(self, ocp_health):
        """
         Verify the openshift API server health status (bool) is returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of API server")
        is_api_server_healthy = ocp_health.check_api_server_health()
        assert isinstance(is_api_server_healthy, bool)

    def test_check_web_console_health(self, ocp_health):
        """
         Verify the openshift web console health status (bool) is returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of web console")
        is_web_console_healthy = ocp_health.check_web_console_health()
        assert isinstance(is_web_console_healthy, bool)

    @pytest.mark.skip(reason="MPQEENABLE-433 Health checker failures - OCP 4.5.30")
    def test_check_cluster_version_operator_health(self, ocp_health):
        """
         Verify the openshift ClusterVersion operator health status (bool) is returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of cluster version operator")
        is_cluster_version_operator_healthy = ocp_health.check_cluster_version_operator_health()
        assert isinstance(is_cluster_version_operator_healthy, bool)

    def test_check_control_plane_status(self, ocp_health):
        """
         Verify the openshift ControlPlane health status (bool) and failure components (list) are returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of control plane status")
        all_control_plane_components_healthy, unhealthy_components_list = ocp_health.check_control_plane_status()
        assert isinstance(all_control_plane_components_healthy, bool)
        assert isinstance(unhealthy_components_list, list)
        if all_control_plane_components_healthy:
            assert len(unhealthy_components_list) == 0
        else:
            assert len(unhealthy_components_list) > 0

    def test_check_cluster_operators_health(self, ocp_health):
        """
        Verify the openshift health status of all cluster operators(bool) and failure operators (list) if any
        are returned
        :param ocp_health: OcpHealthChecker class object
        :return: None
        """
        logger.info("Check health of cluster operator")
        all_cluster_operators_healthy, unhealthy_operators_list = ocp_health.check_cluster_operators_health()
        isinstance(all_cluster_operators_healthy, bool)
        isinstance(unhealthy_operators_list, list)
        if all_cluster_operators_healthy:
            assert len(unhealthy_operators_list) == 0
        else:
            assert len(unhealthy_operators_list) > 0
