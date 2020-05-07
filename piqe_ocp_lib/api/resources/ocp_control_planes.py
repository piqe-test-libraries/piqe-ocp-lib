from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from kubernetes.client.rest import ApiException
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpControlPlane(OcpBase):
    """
        OcpControlPlane class extends OcpBase and encapsulates all methods
        related to managing Openshift Control Planes.
        :param kube_config_file: A kubernetes config file.
        :return: None
        """

    def __init__(self, kube_config_file=None):
        super(OcpControlPlane, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'v1'
        self.kind = 'ComponentStatus'
        self.ocp_control_plane = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_control_plane_component(self, name):
        """
        Get specific cluster operator
        :param name: (str) Name of the cluster operator i.e. authentication
        :return: (Dict) API Response on success or None on Failure
        """
        control_plane_component = None
        try:
            control_plane_component = self.ocp_control_plane.get(name=name)
        except ApiException as e:
            logger.error("Exception while getting control plane component %s : %s\n", name, e)

        return control_plane_component

    def get_all_control_plane_components(self):
        control_plane_components = None
        try:
            control_plane_components = self.ocp_control_plane.get()
        except ApiException as e:
            logger.error("Exception while getting control plane components : %s\n", e)

        return control_plane_components

    def get_control_plane_components_name(self):
        control_plane_components_name = list()
        try:
            control_plane_components = self.ocp_control_plane.get()
        except ApiException as e:
            logger.error("Exception while getting control plane components : %s\n", e)

        if control_plane_components:
            for control_plane_component in control_plane_components.items:
                control_plane_components_name.append(control_plane_component["metadata"]["name"])

        return control_plane_components_name
