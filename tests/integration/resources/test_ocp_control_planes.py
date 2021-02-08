import logging
import pytest
import random
from piqe_ocp_lib.api.resources.ocp_control_planes import OcpControlPlane
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)

pytest.control_plane_components_names = None


@pytest.fixture(scope="session")
def ocp_control_plane(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpControlPlane(kube_config_file=kube_config_file)


class TestOcpControlPlane:

    def test_get_control_plane_components_name(self, ocp_control_plane):
        """
        Verify that openshift control plane components name are returned
        :param ocp_control_plane: OcpControlPlane class object
        :return:
        """
        logger.info("Get cluster control plane components name ONLY")
        pytest.control_plane_components_names = ocp_control_plane.get_control_plane_components_name()
        logger.debug("Cluster Control Plane Components Names : %s", pytest.control_plane_components_names)

        if len(pytest.control_plane_components_names) == 0:
            assert False, "Failed to get control plane components"

    def test_get_control_plane_component(self, ocp_control_plane):
        """
        Verify that specific openshift control plane component response is returned
        :param ocp_control_plane: OcpControlPlane class object
        :return:
        """
        logger.info("Get specific control plane components details")
        component_name = random.choice(pytest.control_plane_components_names)
        component_detail = ocp_control_plane.get_control_plane_component(name=component_name)
        logger.debug("%s control plane component detail : %s\n", component_name, component_detail)

        if not component_detail and not component_detail["metadata"]["name"] == component_name:
            assert False, f"Failed to get {component_name} control plane component"

    def test_get_all_control_plane_components(self, ocp_control_plane):
        """
        Verify that openshift control plane components response are returned
        :param ocp_control_plane: OcpControlPlane class object
        :return:
        """
        logger.info("Get al control plane components details")
        components_detail = ocp_control_plane.get_all_control_plane_components()
        logger.debug("Components details : %s", components_detail)

        if not components_detail and len(components_detail.items) == 0:
            assert False, "Failed to get control plane components"
