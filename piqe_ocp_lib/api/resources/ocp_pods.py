import logging

from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpBase

logger = logging.getLogger(__loggername__)


class OcpPods(OcpBase):
    """
    OcpPods Class extends OcpBase and encapsulates all methods
    related to managing Openshift pods.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        self.kube_config_file = kube_config_file
        OcpBase.__init__(self, kube_config_file=self.kube_config_file)
        self.core_v1 = client.CoreV1Api(api_client=self.k8s_client)
        self.api_version = "v1"
        self.kind = "Pod"
        self.ocp_pods = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_a_pod_from_definition(self, definition):
        """
        Create a pod with specified definition
        :param definition: Definition for additional network interface in dict form
        :return: api_response
        """
        api_response = None
        try:
            api_response = self.ocp_pods.create(body=definition)
        except ApiException as e:
            print("Exception while creating pods: %s\n", e)
        return api_response

    def list_pods_in_a_namespace(self, namespace, label_selector=""):
        """
        Method to list details for all or a specific type of pod within
        a namespace. If no parameter is given, it defaults to listing
        details for all pod types.
        :param namespace: The namespace containing the targeted pod
        :param label_selector: used to filter the types of pods
                               to be retrieved
        :return: A V1PodList object on success. None on failure
        """
        api_response = None
        try:
            api_response = self.ocp_pods.get(namespace=namespace, label_selector=label_selector)
        except ApiException as e:
            logger.error("Exception while getting pods: %s\n", e)
        return api_response

    def get_all_pod_names_in_a_namespace(self, namespace):
        """
        Method to list all pod names pod within
        a namespace. If no parameter is given, it defaults to listing
        details for all pod types.
        :param namespace: The namespace containing the targeted pod
        :return: List of pod names OR Empty list if there are no pods in namespace
        """
        list_of_pod_names = list()
        api_response = self.list_pods_in_a_namespace(namespace=namespace)
        if api_response:
            for item in api_response.items:
                list_of_pod_names.append(item["metadata"]["name"])
        return list_of_pod_names

    def list_pods_in_a_deployment(self, namespace, dc):
        """
        Method that returns a list of Pods belonging to
        a Deployment Config in a specific namespace
        :param namespace: The namespace where the dc is deployed
        :param dc: The Deployment Config for which we want to
                   retrieve the Pods
        :return: The name of the initial pod created as part of a deployment config.
                None on failure.
        """
        pods_in_dc = None
        pods_in_namespace = self.list_pods_in_a_namespace(namespace=namespace, label_selector="deploymentconfig")
        if pods_in_namespace:
            pod_list = pods_in_namespace.items
            pods_in_dc = [
                pod.metadata.name
                for pod in pod_list
                if pod.metadata.annotations["openshift.io/deployment-config.name"] == dc
            ]
        return pods_in_dc

    def list_all_pods_in_all_namespaces(self):
        """
        Method that returns a list of All Pods belonging to
        a Deployment Config in all namespaces
        :return: The names of all the pods for all namespaces.
                 None on failure.
        """
        api_response = None
        try:
            api_response = self.ocp_pods.get()
        except ApiException as e:
            logger.error("Exception while getting pods: %s\n", e)
        return api_response

    def delete_pod_in_a_namespace(self, namespace, name, label_selector=""):
        """
        Method that deletes a specific pod in a specific namespace
        :param namespace:  The namespace where the pod is deployed
        :param name: The name of the pod to delete
        :param label_selector: used to filter the types of pods
                               to be deleted
        :return: PodObject on success, None on failure
        """
        api_response = None
        try:
            api_response = self.ocp_pods.delete(namespace=namespace, name=name, label_selector=label_selector)
        except ApiException as e:
            logger.error("Exception deleting pod: %s\n", e)
        return api_response

    def is_pod_ready(self, namespace, pod_name, timeout):
        """
        Method that watches a pod in a specific namespace
        for changes
        :param timeout: timeout in sec
        :param namespace: The namespace where the targeted pod resides
        :param pod_name: The name of the pod to watch
        :return: boolean
        """
        logger.info("Watching pod %s for readiness" % pod_name)
        pod_ready = False
        field_selector = "metadata.name={}".format(pod_name)
        for event in self.ocp_pods.watch(namespace=namespace, field_selector=field_selector, timeout=timeout):
            for pod_condition in event["object"]["status"]["conditions"]:
                if pod_condition["status"] == "True" and pod_condition["type"] == "Ready":
                    logger.info("Pod %s is in %s state", pod_name, pod_condition["type"])
                    pod_ready = True
                    return pod_ready
        logger.error("Pod %s is in %s state", pod_name, pod_condition["type"])
        return pod_ready

    def execute_command_on_pod(self, pod_name, namespace, command):
        """
        Execute command on pod
        :param pod_name: (str) Name of the Pods
        :param namespace: (str) Namespace where pod has been deployed
        :param command: (str | list of comma separated str if cmd is space separated ) Command to execute
        :return: (str) Command response
        """
        cmd_response = None
        try:
            cmd_response = stream(
                self.core_v1.connect_get_namespaced_pod_exec,
                name=pod_name,
                command=command,
                namespace=namespace,
                stderr=True,
                stdin=True,
                stdout=True,
                tty=False,
            )
        except ApiException as e:
            logger.error("Exception while calling pod : %s\n", e)
        return cmd_response

    def get_pod_node(self, namespace, pod_name):
        """
        Method that gets node of the specific pod in a specific namespace
        :param namespace:  The namespace where the pod is deployed
        :param pod_name: The name of the pod
        :return: node hostname on success, None on failure
        """
        api_response = None
        node_name = None
        try:
            api_response = self.ocp_pods.get(namespace=namespace, name=pod_name)
        except ApiException as e:
            logger.error("Exception while getting pods: %s\n", e)
        if api_response is not None:
            if api_response.spec["nodeName"]:
                node_name = api_response.spec["nodeName"]
        return node_name
