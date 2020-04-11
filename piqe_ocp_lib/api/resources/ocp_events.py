from .ocp_base import OcpBase
from .ocp_pods import OcpPods
from kubernetes.client.rest import ApiException
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpEvents(OcpBase):
    """
    OcpEvents Class extends OcpBase and encapsulates all methods
    related to managing Openshift events.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        self.kube_config_file = kube_config_file
        OcpBase.__init__(self, kube_config_file=self.kube_config_file)
        self.ocp_pod_obj = OcpPods(kube_config_file=self.kube_config_file)
        self.api_version = 'v1'
        self.kind = 'Event'
        self.ocp_events = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def list_dc_events_in_a_namespace(self, namespace, dc):
        """
        Method that lists the events for a deploymentconfig in a specific namespace
        :param namespace: The namespace where the targeted dc resides
        :param dc: The Deployment Config whose pods we want to retrieve
                   events for.
        :return: A list of objects of type V1Event on success. None on failure.
        """
        api_response = None
        dc_events = None
        try:
            api_response = self.ocp_events.get(namespace=namespace)
        except ApiException as e:
            logger.error("Exception while getting dc events: %s\n", e)
        if api_response:
            dc_events = [ev for ev in api_response.items if (
                ev.involvedObject.kind == 'DeploymentConfig' and ev.involvedObject.name == dc)]
        return dc_events

    def list_pod_events_in_a_namespace(self, namespace, dc):
        """
        Method that lists the events for pods belonging to a specific
        deploymentconfig in a specific namespace
        :param namespace: The namespace where the targeted dc resides
        :param dc: The Deployment Config whose pods we want to retrieve
                   events for.
        :return: A list of objects of type V1Event on success. None on failure.
        """
        api_response = None
        pod_events = None
        try:
            pods_in_dc = self.ocp_pod_obj.list_pods_in_a_deployment(namespace, dc)
            api_response = self.ocp_events.get(namespace=namespace)
        except ApiException as e:
            logger.error("Exception while getting pod events: %s\n", e)
        if api_response:
            pod_events = [ev for ev in api_response.items if (
                ev.involvedObject.kind == 'Pod' and ev.involvedObject.name in pods_in_dc)]
        return pod_events
