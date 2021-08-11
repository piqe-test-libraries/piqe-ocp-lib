import logging
import warnings

import requests
from urllib3.exceptions import InsecureRequestWarning

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from piqe_ocp_lib.api.resources.ocp_cluster_operators import OcpClusterOperator
from piqe_ocp_lib.api.resources.ocp_cluster_versions import OcpClusterVersion
from piqe_ocp_lib.api.resources.ocp_configs import OcpConfig
from piqe_ocp_lib.api.resources.ocp_control_planes import OcpControlPlane
from piqe_ocp_lib.api.resources.ocp_deploymentconfigs import OcpDeploymentconfigs
from piqe_ocp_lib.api.resources.ocp_nodes import OcpNodes
from piqe_ocp_lib.api.resources.ocp_pods import OcpPods
from piqe_ocp_lib.api.resources.ocp_routes import OcpRoutes
from piqe_ocp_lib.api.resources.ocp_secrets import OcpSecret

warnings.simplefilter("ignore", InsecureRequestWarning)

logger = logging.getLogger(__loggername__)


class OcpHealthChecker(OcpBase):
    """
    OcpHealthChecker will check the health of certain critical openshift components.
    - Node/Controller
    - Router
    - ImageRegistry
    - Persistence Storage for ImageRegistry
    - API Server
    - Web Console
    - Cluster Version
    - Control Planes
    - Cluster Operators

    Every components health check returns overall health of that component (bool) and optional unhealthy components
    (list or dict). Optional unhealthy components will be display in tabular format when we check the health of
    openshift cluster.

    """

    def __init__(self, kube_config_file):
        self.kube_config_file = kube_config_file
        super().__init__(kube_config_file=self.kube_config_file)
        self.ocp_node = OcpNodes(kube_config_file=self.kube_config_file)
        self.ocp_cluster_operator = OcpClusterOperator(kube_config_file=self.kube_config_file)
        self.ocp_control_plane = OcpControlPlane(kube_config_file=self.kube_config_file)
        self.ocp_cluster_version = OcpClusterVersion(kube_config_file=self.kube_config_file)
        self.ocp_route = OcpRoutes(kube_config_file=self.kube_config_file)
        self.ocp_pod = OcpPods(kube_config_file=self.kube_config_file)
        self.ocp_deployment = OcpDeploymentconfigs(kind="Deployment", kube_config_file=self.kube_config_file)
        self.ocp_config = OcpConfig(
            kind="Config", api_version="imageregistry.operator.openshift.io/v1", kube_config_file=self.kube_config_file
        )
        self.ocp_secret = OcpSecret(kube_config_file=self.kube_config_file)

    def check_node_health(self):
        """
        Check health of each cluster node
        Methods checks for:
            - DiskPressure: All have sufficient disk space.
            - MemoryPressure: All have sufficient memory
            - PIDPressure: All have sufficient number processes are running
            - If ALL above is False and NodeReadyStatus is True, then node is in ready(healthy) state
        :return: Return tuple of all_nodes_healthy(boolean) and node_health_info(dict of node name and failure reason)
        """
        logger.info("Checking all cluster nodes health")
        unhealthy_node_info = dict()
        all_nodes_healthy = False
        individual_node_health_status_list = list()
        node_list_info = self.ocp_node.get_all_nodes()
        if node_list_info:
            for node_info in node_list_info.items:
                temp_list = list()
                for condition in node_info.status.conditions:
                    if condition["type"] == "Ready":
                        individual_node_health_status_list.append(condition["status"])
                    if condition["type"] == "Ready" and condition["status"] != "True":
                        temp_list.append({"NodeReadyStatus": condition["status"]})
                    elif condition["type"] == "MemoryPressure" and condition["status"] == "True":
                        temp_list.append({"MemoryPressure": "The node memory is low"})
                    elif condition["type"] == "DiskPressure" and condition["status"] == "True":
                        temp_list.append({"DiskPressure": "The disk capacity is low"})
                    elif condition["type"] == "PIDPressure" and condition["status"] == "True":
                        temp_list.append({"PIDPressure": "There are too many processes on the node"})

                unhealthy_node_info[node_info["metadata"]["name"]] = temp_list

        logger.info("Check overall health of cluster nodes by checking each node health")
        if (
            len(set(individual_node_health_status_list)) == 1
            and list(set(individual_node_health_status_list))[0] == "True"
        ):
            all_nodes_healthy = True

        return all_nodes_healthy, unhealthy_node_info

    def check_router_health(self):
        """
        Check openshift router health
        - Check if router pod is running fine in openshift-ingress namespace
        - Check if deployments of router has matching number of replicas
        :return:Return tuple of bool (is_router_healthy) and dict (unhealthy_router_info)
        """
        logger.info("Check the health of openshift router operator pod")
        is_router_healthy = False
        unhealthy_router_info = dict()
        is_router_pod_healthy = False
        is_replicas_count_matching = False
        unhealthy_pods = dict()
        pods_response = self.ocp_pod.list_pods_in_a_namespace(namespace="openshift-ingress")
        for pod in pods_response.items:
            for condition in pod["status"]["conditions"]:
                if condition["type"] == "Ready" and condition["status"] == "False":
                    unhealthy_pods[pod["metadata"]["name"]] = condition["status"]

        if len(unhealthy_pods.values()) == 0:
            is_router_pod_healthy = True
        # Get unhealthy pod names
        unhealthy_pod_names = list()
        for key, value in unhealthy_pods.items():
            unhealthy_pod_names.append(key)
        unhealthy_router_info.update({"router_pod": unhealthy_pod_names})
        logger.info("Is router pod/s healthy : %s", is_router_pod_healthy)

        logger.info("Check replicas count of openshift router deployment are matching")
        deployment_response = self.ocp_deployment.list_all_deployments_in_a_namespace(namespace="openshift-ingress")
        for deployment in deployment_response.items:
            if deployment.metadata.name == "router-default":
                replicas = deployment.status.replicas
                available_replicas = deployment.status.availableReplicas
                ready_replicas = deployment.status.readyReplicas
        if replicas == available_replicas == ready_replicas:
            is_replicas_count_matching = True
        # If replicas count doesn't match, add them into unhealthy component list
        if not is_replicas_count_matching:
            unhealthy_router_info.update({"router_replicas": is_replicas_count_matching})
        logger.info("Is router deployment replicas count matching : %s", is_replicas_count_matching)

        logger.info("Check overall health of router operator")
        if is_router_pod_healthy and is_replicas_count_matching:
            is_router_healthy = True

        return is_router_healthy, unhealthy_router_info

        logger.info("Check overall health of router operator")
        if is_router_pod_healthy and is_replicas_count_matching:
            is_router_healthy = True

        return is_router_healthy, unhealthy_router_info

    def check_image_registry_health(self):
        """
        Check openshift cluster image registry
        - Check if image registry pod is running fine in openshift-image-registry namespace
        - Check if deployments of image registry has matching number of replicas
        :return:
        """
        logger.info("Check health of openshift image registry pods")
        is_image_registry_healthy = False
        unhealthy_image_registry_info = dict()
        is_image_registry_pods_healthy = False
        unhealthy_pods = dict()
        pods_response = self.ocp_pod.list_pods_in_a_namespace(namespace="openshift-image-registry")
        for pod in pods_response.items:
            if "cluster-image-registry-operator" in pod.metadata.name or "image-registry" in pod.metadata.name:
                for condition in pod["status"]["conditions"]:
                    if condition["type"] == "Ready" and condition["status"] == "False":
                        unhealthy_pods[pod["metadata"]["name"]] = condition["status"]

        if len(unhealthy_pods.values()) == 0:
            is_image_registry_pods_healthy = True
        # Get unhealthy pod names
        unhealthy_pod_names = list()
        for key, value in unhealthy_pods.items():
            unhealthy_pod_names.append(key)
        unhealthy_image_registry_info.update({"image_registry_pod": unhealthy_pod_names})
        logger.info("Is image registry pod/s healthy : %s", is_image_registry_pods_healthy)

        logger.info("Check replicas count of openshift image registry deployment are matching")
        is_replicas_count_matching = False
        replica_count_dict = dict()
        deployment_response = self.ocp_deployment.list_all_deployments_in_a_namespace(
            namespace="openshift-image-registry"
        )
        for deployment in deployment_response.items:
            if (
                deployment.metadata.name == "cluster-image-registry-operator"
                or deployment.metadata.name == "image-registry"
            ):
                replicas = deployment.status.replicas
                available_replicas = deployment.status.availableReplicas
                ready_replicas = deployment.status.readyReplicas

            if replicas == available_replicas == ready_replicas:
                is_replicas_count_matching_for_each_image_registry = True
            replica_count_dict[deployment.metadata.name] = is_replicas_count_matching_for_each_image_registry
            logger.info(
                "Is replicas count for %s matching? : %s",
                deployment.metadata.name,
                is_replicas_count_matching_for_each_image_registry,
            )

        if all(val for val in replica_count_dict.values()):
            is_replicas_count_matching = True
        # If replicas count doesn't match, add them into unhealthy component list
        if not is_replicas_count_matching:
            unhealthy_image_registry_info.update({"image_registry_replicas": is_replicas_count_matching})
        logger.info("Is replicas count matching for all image registry deployment : %s", is_replicas_count_matching)

        logger.info("Check overall health of image registry operator by checking pod/s status and replicas count match")
        if is_image_registry_pods_healthy and is_replicas_count_matching:
            is_image_registry_healthy = True

        return is_image_registry_healthy, unhealthy_image_registry_info

    def check_persistence_storage_for_image_registry(self):
        """
        Check if persistence storage configure for cluster image registry
        - Check managementState of image-registry. IPI installation has default "Managed".
          UPI installation has default "Removed". managementState field should "Managed".
            Managed: The Operator updates the registry as configuration resources are updated.
            Unmanaged: The Operator ignores changes to the configuration resources.
            Removed: The Operator removes the registry instance and tear down any storage that the Operator provisioned.
        - Check if persistence storage configured for image registry
        :return: (boolean) Return True if persistence storage configured for image registry otherwise False.

        NOTE : If persistence storage is not configured for image registry doesn't mean unhealthy. It's a WARNING. If
        persistence storage is not configure for image registry, Images will be inaccessible after reboot.
        """
        is_image_registry_storage_configured = False
        is_management_state_correct = False
        is_persistence_storage_configured = True
        logger.info("Check managementState for image registry")
        image_config_response = self.ocp_config.get_ocp_config(name="cluster")
        if image_config_response["spec"]["managementState"] == "Managed":
            is_management_state_correct = True
        logger.info("Is managementState correct : %s", {is_management_state_correct})

        logger.info("Check if persistence storage configured for image registry")
        if "emptyDir" in dict(image_config_response["spec"]["storage"]):
            is_persistence_storage_configured = False
        logger.info("Is persistence Storage Configured: %s", is_persistence_storage_configured)

        if is_management_state_correct and is_persistence_storage_configured:
            is_image_registry_storage_configured = True

        return is_image_registry_storage_configured

    def check_api_server_health(self):
        """
        Check openshift apiserver is reachable and  healthy
        :return: (boolean) Return True if api server is healthy otherwise False
        """
        status_codes = dict()
        is_api_server_healthy = False
        kubeconfig_data = self.get_data_from_kubeconfig_v4()

        logger.info("Check health of API Server")
        api_server_url = kubeconfig_data["api_server_url"]
        final_api_server_url = api_server_url + "/healthz"
        logger.info("API Server URL : %s", final_api_server_url)
        bearer_token = self.ocp_secret.get_long_live_bearer_token()
        headers = {"Authorization": "Bearer " + bearer_token}

        # Suppress only the single warning from urllib3 needed.
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        api_server_response = requests.get(final_api_server_url, headers=headers, verify=False)
        logger.info("API Server Status Code : %s", api_server_response.status_code)
        status_codes["api_server_status"] = api_server_response.status_code

        for key, value in status_codes.items():
            if value in range(200, 300):
                is_api_server_healthy = True

        return is_api_server_healthy

    def check_web_console_health(self):
        """
        Check if web console is reachable and healthy
        :return:(boolean) Return True if web console is healthy otherwise False
        """
        status_codes = dict()
        is_web_console_healthy = False

        logger.info("Check health of web-console")
        web_console_route = self.ocp_route.get_route_in_namespace(namespace="openshift-console", route_name="console")
        web_console_url = "https://" + web_console_route + ":443" + "/healthz"
        logger.info("Web Console URL : %s", web_console_url)

        # Suppress only the single warning from urllib3 needed.
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        web_console_response = requests.get(web_console_url, verify=False)
        logger.info("Web Console Status Code : %s", web_console_response.status_code)
        status_codes["web_console_status"] = web_console_response.status_code

        for key, value in status_codes.items():
            if value in range(200, 300):
                is_web_console_healthy = True

        return is_web_console_healthy

    def check_cluster_version_operator_health(self):
        """
        Check ClusterVersion operator health
        :return: (boolean) Return
        """
        logger.info("Check health of ClusterVersion operator")
        is_cluster_version_operator_healthy = False

        cluster_version_response = self.ocp_cluster_version.get_cluster_version()
        for cluster_version in cluster_version_response.items:
            if cluster_version["metadata"]["name"] == "version":
                for condition in cluster_version["status"]["conditions"]:
                    if condition["type"] == "Available" and condition["status"] == "True":
                        is_cluster_version_operator_healthy = True

        return is_cluster_version_operator_healthy

    def check_control_plane_status(self):
        """
        Check health of cluster control plane components
        Command : "oc get cs OR oc get componentstatus"
        :return: (tuple) Return tuple of overall health of control plane component (boolean) and list of unhealthy
        components if any
        """
        logger.info("Checking control plan status")
        all_control_plane_components_healthy = False
        unhealthy_components_list = list()
        control_plane_components = self.ocp_control_plane.get_all_control_plane_components()
        if control_plane_components:
            for control_plane_component in control_plane_components.items:
                for condition in control_plane_component.conditions:
                    if condition["type"] != "Healthy" and not condition["status"] == "False":
                        unhealthy_components_list.append(control_plane_component["metadata"]["name"])

        # Set control plane health by checking all control plane components health
        if len(unhealthy_components_list) == 0:
            all_control_plane_components_healthy = True

        return all_control_plane_components_healthy, unhealthy_components_list

    def check_cluster_operators_health(self):
        """
        Check health of cluster operator
        Command : "oc get co OR oc get clusteroperator"
        :return: (tuple) Return overall health of cluster operator (boolean) and list of unhealthy operator if any
        """
        logger.info("Checking all cluster operators health")
        all_cluster_operators_healthy = False
        unhealthy_operators_list = list()
        cluster_operators = self.ocp_cluster_operator.get_all_cluster_operators()
        if cluster_operators:
            for cluster_operator in cluster_operators.items:
                for condition in cluster_operator.status.conditions:
                    if condition["type"] == "Available" and condition["status"] == "False":
                        unhealthy_operators_list.append(cluster_operator["metadata"]["name"])

        # Set cluster operator health status by checking all operator are health
        if len(unhealthy_operators_list) == 0:
            all_cluster_operators_healthy = True

        return all_cluster_operators_healthy, unhealthy_operators_list
