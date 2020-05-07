from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from kubernetes.client.rest import ApiException
import logging
from time import sleep, time
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpDeploymentconfigs(OcpBase):
    """
    OcpDeploymentconfigs Class extends OcpBase and encapsulates all methods
    related to managing Openshift DeploymentConfigs/Deployments.
    :param api_version: (str) kubernetes/openshift api version
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kind="DeploymentConfig", kube_config_file=None):
        super(OcpDeploymentconfigs, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'v1'
        self.ocp_dcs = self.dyn_client.resources.get(api_version=self.api_version, kind=kind)

    def check_dc_status_conditions_availability(self, namespace, dc, timeout):
        """
        Helper function that checks the needed parameters in the
        status object belonging to a deployment config (dc) are
        available before we make any subsequent calls that depend
        on the availability of those parameters. Specifically, we
        are looking for two objects under the conditions list,
        progression and availability
        :param namespace: The namespace containing the targeted
                          deployment config
        :param dc: The targeted deployment config
        :return: Bool
        """
        end = time() + timeout
        while time() < end:
            try:
                current_dc = self.ocp_dcs.get(namespace=namespace, name=dc)
            except ApiException as e:
                logger.error("Exception while getting deploymentconfigs: %s\n", e)
                return False
            sleep(30)
            scs = current_dc.status.conditions
            if scs and scs[0]["status"] == "True" and scs[0]["type"] == "Available":
                logger.debug("Pods status: %s", scs)
                return True
        logger.debug("Pods conditions: %s", scs)
        logger.error("Pod/s fail to start in %s min", timeout)
        return False

    def is_dc_ready(self, namespace, dc, timeout):
        """
        Method that watches a deploymentconfig in a specific namespace
        for changes
        :param namespace: The namespace where the targeted dc resides
        :param dc: The name of the deploymentconfig to watch
        :return: boolean
        """
        logger.info("Watching deploymentconfig %s for readiness" % dc)
        dc_ready = False
        field_selector = "metadata.name=%s" % dc
        for event in self.ocp_dcs.watch(namespace=namespace, field_selector=field_selector, timeout=timeout):
            status_conditions_list = event['object']['status']['conditions']
            availability = [s for s in status_conditions_list if s.type == 'Available'][0]
            progression = [s for s in status_conditions_list if s.type == 'Progressing'][0]
            if availability.status == 'True' and progression.status == 'True':
                logger.info("Pods for deploymentconfig %s are up" % dc)
                dc_ready = True
                return dc_ready
        return dc_ready

    def update_deployment_replicas(self, namespace, dc, replicas):
        """
        Method to change number of replicas for a deployment
        :param namespace: The namespace containing the targeted
                          deployment config
        :param dc: The targeted deployment config
        :param replicas: The desired number of replicas
        :return: A V1DeploymentConfig object
        """
        body = {"spec": {"replicas": replicas}}
        api_response = None
        try:
            api_response = self.ocp_dcs.patch(name=dc, namespace=namespace, body=body)
        except ApiException as e:
            logger.error("Exception while updating deploymentconfigs: %s\n", e)
        return api_response

    def label_dc(self, namespace, dc, labels):
        """
        Method that patches a Deployment Config as a means
        to apply a label to it.
        :param namespace: The name of the namespace containing the targeted dc
        :param dc: The deployment config to be labeled
        :param labels: A dictionary containing the key,val labels
        :return: A V1DeploymentConfig object
        """
        body = {'metadata': {'labels': labels}}
        api_response = None
        try:
            api_response = self.ocp_dcs.patch(name=dc, namespace=namespace, body=body)
        except ApiException as e:
            logger.error("Exception while labeling deploymentconfigs: %s\n", e)
        return api_response

    def patch_dc(self, namespace, dc, body):
        """
        Method that generically patches a Deployment Config
        :param namespace: The name of the namespace containing the targeted dc
        :param dc: The deployment config to be patched
        :param body: A dictionary containing the keys and values to apply
        :return: A V1DeploymentConfig object
        """
        api_response = None
        try:
            api_response = self.ocp_dcs.patch(name=dc, namespace=namespace, body=body)
        except ApiException as e:
            logger.error("Exception while patching deploymentconfigs: %s\n", e)
        return api_response

    def list_deployment_in_a_namespace(self, namespace, dc):
        """
        Method to list details of a deployment config
        within a namespace
        :param namespace: The namespace containing the targeted
                          deployment config.
        :param dc: The targeted deployment config to be listed
        :return: A V1DeploymentConfig object on success. None on failure
        """
        api_response = None
        try:
            api_response = self.ocp_dcs.get(namespace=namespace, name=dc)
        except ApiException as e:
            logger.error("Exception while getting deploymentconfigs: %s\n", e)
        return api_response

    def list_all_deployments_in_a_namespace(self, namespace):
        """
        Method to list details of a deployment config
        within a namespace
        :param namespace: The namespace containing the deployment configs.
        :return: A V1DeploymentConfig object on success. None on failure
        """
        api_response = None
        try:
            api_response = self.ocp_dcs.get(namespace=namespace)
        except ApiException as e:
            logger.error("Exception while getting deploymentconfigs: %s\n", e)
        return api_response

    def list_deployments_in_all_namespaces(self, label_selector=''):
        """
        Method that lists all deployment configs across all
        namespaces in a cluster.
        :param label_selector: Used to filter the types of dcs
                               to be selected.
        :return: A V1DeploymentConfigList object on success. None on failure
        """
        api_response = None
        try:
            api_response = self.ocp_dcs.get(label_selector=label_selector)
        except ApiException as e:
            logger.error("Exception while getting deploymentconfigs: %s\n", e)
        return api_response

    def find_unhealthy_dcs_in_namespace_list(self, dc_list):
        """
        :param dc_list: A list of objects of type V1DeploymentConfig
        :return: A list of objects of type DeploymentConfig if any.
        """
        # Every dc object has a status key containing a conditions list.
        # The conditions list contains exactly two objects of type v1.DeploymentCondition,
        # the first object of the two being of type 'Available' and the second 'Progressing'
        # If neither has a False status, we treat the corresponding dc as unhealthy.
        unhealthy_dcs = []
        for dc in dc_list:
            if dc.status.conditions[0].status == 'False' and dc.status.conditions[1].status == 'False':
                unhealthy_dcs.append(dc)
        return unhealthy_dcs

    def read_dc_log(self, namespace, dc, tail_lines=6):
        """
        Method to read the logs of a deployment config
        within a namespace. Returns a list of lines of
        requested log file.
        :param namespace: The namespace where the targeted dc resides
        :param dc: The targeted deployment config
        :param tail_lines: The number of most recent lines in the log
                           to be displayed.
        :return: A list of strings.
        """
        try:
            api_response = self.ocp_dcs.log.get(namespace=namespace, name=dc)
        except ApiException as e:
            logger.error("Exception while getting deploymentconfig log: %s\n", e)
        dc_log = api_response.split('\n')[-tail_lines:-1]
        return dc_log
