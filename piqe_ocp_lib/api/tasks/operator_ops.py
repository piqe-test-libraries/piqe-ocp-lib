import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpBase, OcpProjects
from piqe_ocp_lib.api.resources.ocp_operators import (
    ClusterServiceVersion,
    OperatorGroup,
    OperatorhubPackages,
    Subscription,
)

logger = logging.getLogger(__loggername__)


class OperatorInstaller(OcpBase):
    def __init__(self, kube_config_file):
        super(OperatorInstaller, self).__init__(kube_config_file=kube_config_file)
        self.og_obj = OperatorGroup(kube_config_file=self.kube_config_file)
        self.sub_obj = Subscription(kube_config_file=self.kube_config_file)
        self.ohp_obj = OperatorhubPackages(kube_config_file=self.kube_config_file)
        self.proj_obj = OcpProjects(kube_config_file=self.kube_config_file)
        self.csv = ClusterServiceVersion(self.kube_config_file)

    def _derive_install_mode_from_target_namespaces(self, operator_name, target_namespaces):
        """
        Length of target_namespaces list enables us to derive the appropriate install mode
        Look at the length of the target_namespaces list:
            1. If it's zero, then we verify if 'AllNamespaces' is supported.
            2. If length is 1, then we verify if 'SingleNamespace' is supported.
            3. If length > 1, then we verify 'MultiNamespace' is supported.
        """
        target_namespaces_count = len(target_namespaces)
        if target_namespaces_count == 0:
            install_mode = "AllNamespaces"
        elif target_namespaces_count == 1:
            install_mode = "SingleNamespace"
        elif target_namespaces_count > 1:
            install_mode = "MultiNamespace"
        return install_mode

    def _create_og(self, operator_name, install_mode, target_namespaces):
        """
        A helper method that creates a placeholder project that will contain the
        subscription and operator group objects necessary to install an operator
        For openshift 4.1, the operator installation only succeeds if these objects
        are installed in the opeshift-marketplace namespace. In openshift 4.2+, we
        create a project with the following naming convention:
        test + operator name + install mode + og-sub-project
        """
        og_name = f"{operator_name}-{install_mode.lower()}-og"
        og_namespace = f"test-{operator_name}-{install_mode.lower()}-og-sub-project"
        logger.info(f"Creating Project: {og_namespace} that will hold the subscription and operator group")
        assert self.proj_obj.create_a_project(og_namespace)
        assert self.og_obj.create_operator_group(og_name, og_namespace, target_namespaces)
        return og_name, og_namespace

    def add_operator_to_cluster(self, operator_name, target_namespaces=[]):
        """
        Install an operator in a list of targeted namespaces
        :param operator_name: (required | str) The name of the operator to be installed
        :param target_namespaces: (optional | list) A list of namespace/Projects where want the
                                   operator to be enabled in. If left unspecified, the operartor
                                   will be installed/enabled throughout the entire cluster.
        """

        pkg_obj = self.ohp_obj.get_package_manifest(operator_name)

        if not pkg_obj:
            err_msg = f"A package manifest for {operator_name} could not be found"
            logger.exception(err_msg)
            raise ApiException(err_msg)

        install_mode = self._derive_install_mode_from_target_namespaces(operator_name, target_namespaces)
        _, og_namespace = self._create_og(operator_name, install_mode, target_namespaces)
        self.sub_obj.create_subscription(operator_name, install_mode, og_namespace)

        return True

    def verify_operator_installed(self, operator_name, operator_namespace):
        """
        Check if operator is installed and returned true or false
        :param operator_name: name of the operator.
        :param operator_namespace: namespace of the operator
        return: object of values of csv
        """
        csv = self.csv
        csv_resp = csv.get_cluster_service_version(operator_name, operator_namespace)
        return csv_resp

      

    def delete_operator_from_cluster(self, operator_name: str, namespace: str) -> bool:
        """
        Uninstall an operator from a cluster
        :param operator_name: name of the operator
        :param namespace: name of the namespace the operator is installed
        :return: success or failure
        """
        csv = self.csv

        try:
            subscription = self.sub_obj.get_subscription(operator_name, namespace)
            csv_name = subscription.status.currentCSV
        except ApiException:
            logger.error("Failed to retrieve subscription")
            return False

        try:
            self.sub_obj.delete_subscription(operator_name, namespace)
            csv.delete(csv_name, namespace)
        except ApiException:
            logger.error(f"Failed to uninstall operator {operator_name}")
            return False

        return True
