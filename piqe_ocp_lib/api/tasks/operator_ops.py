from piqe_ocp_lib.api.resources import OcpBase, OcpProjects
from piqe_ocp_lib.api.resources.ocp_operators import OperatorhubPackages, \
    Subscription, CatalogSource, OperatorSource, OperatorGroup
from piqe_ocp_lib.api.ocp_exceptions import OcpUnsupportedVersion
from kubernetes.client.rest import ApiException
import logging
import yaml
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OperatorInstaller(OcpBase):
    def __init__(self, kube_config_file):
        super(OperatorInstaller, self).__init__(kube_config_file=kube_config_file)
        self.og_obj = OperatorGroup(kube_config_file=self.kube_config_file)
        self.sub_obj = Subscription(kube_config_file=self.kube_config_file)
        self.os_obj = OperatorSource(kube_config_file=self.kube_config_file)
        self.cs_obj = CatalogSource(kube_config_file=self.kube_config_file)
        self.ohp_obj = OperatorhubPackages(kube_config_file=self.kube_config_file)
        self.proj_obj = OcpProjects(kube_config_file=self.kube_config_file)

    def _source_processor(self, source):
        """
        Takes in a source as eihter a path to a JSON/YAML, or the soure in dict format.
        Currently supported source type is: OperatorSource
        """
        def _source_path_processor(source_path):
            with open(source_path, 'r') as f:
                source = f.read()
            source_dict = dict()
            valid_source = True
            try:
                source_dict = yaml.safe_load(source)
                logger.debug("Successfully loaded the source file.")
            except ValueError as e:
                logger.error("Could not load the source file: {}".format(e))
                valid_source = False
            if valid_source:
                return _source_dict_processor(source_dict)
            else:
                err_msg = "The provided Json/Yaml source file could not be loaded"
                logger.exception(err_msg)
                raise TypeError(err_msg)

        def _source_dict_processor(source_dict):
            """
            A helper method that takes in a source object in dict form. We invoke the
            appropriate create method based on the resource kind and then we finally
            check that a catalogsource object has been created as a result.
            """
            resource_kind = source_dict['kind']
            logger.info("Operator source is of kind: {}".format(resource_kind))
            if resource_kind != 'OperatorSource':
                raise TypeError("The source you provided: {} is an unsupported type".format(resource_kind))
            else:
                resp = self.os_obj.create_operator_source(body=source_dict)
                cs_namespace = resp.metadata.namespace
            logger.info("Cheking if CatalogSource {} exists in namespace {}".format(resp.metadata.name, cs_namespace))
            assert self.cs_obj.is_catalog_source_present(resp.metadata.name, namespace=cs_namespace)
            cs = self.cs_obj.get_catalog_source(resp.metadata.name, namespace=cs_namespace)
            return cs.metadata.name, cs_namespace

        if isinstance(source, str):
            return _source_path_processor(source)
        elif isinstance(source, dict):
            return _source_dict_processor(source)

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
            install_mode = 'AllNamespaces'
        elif target_namespaces_count == 1:
            install_mode = 'SingleNamespace'
        elif target_namespaces_count > 1:
            install_mode = 'MultiNamespace'
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
        og_name = operator_name + '-' + install_mode.lower() + '-og'
        og_namespace = 'test-' + operator_name + '-' + install_mode.lower() + '-og-sub-project'
        logger.info("Creating Project: {} that will hold the subscription and operator group".format(og_namespace))
        assert self.proj_obj.create_a_project(og_namespace)
        assert self.og_obj.create_operator_group(og_name, og_namespace, target_namespaces)
        return og_name, og_namespace

    def add_operator_to_cluster(self, operator_name, source=None, target_namespaces=[]):
        """
        Install an operator in a list of targeted namespaces
        :param operator_name: (required | str) The name of the operator to be installed
        :param source: (optional | str) The source of the operator to be installed. This parameter
                       can be in the form of a path to a source YAML or JSON, or it can also be
                       passed as a dictionary. If not specified, the package is assumed to be already
                       be visible throught the operator hub and so the source can be discovered.
        :param target_namespaces: (optional | list) A list of namespace/Projects where want the
                                   operator to be enabled in. If left unspecified, the operartor
                                   will be installed/enabled throughout the entire cluster.
        """
        if source:
            cs_name, cs_namespace = self._source_processor(source)
            if not self.ohp_obj.watch_package_manifest_present(operator_name):
                err_msg = "A package manifest for {} could not be found".format(operator_name)
                logger.exception(err_msg)
                raise ApiException(err_msg)
        else:
            pkg_obj = self.ohp_obj.get_package_manifest(operator_name)
            if pkg_obj:
                cs_name = pkg_obj.status.catalogSource
                cs_namespace = pkg_obj.metadata.namespace
            else:
                logger.exception(err_msg)
                raise ApiException(err_msg)
        install_mode = self._derive_install_mode_from_target_namespaces(operator_name, target_namespaces)
        og_name, og_namespace = self._create_og(operator_name, install_mode, target_namespaces)
        subscription = self.sub_obj.create_subscription(operator_name, install_mode, og_namespace)
        assert subscription.spec.source == cs_name
        assert subscription.spec.sourceNamespace == cs_namespace
        return True

    def delete_operator_from_cluster(self, operator_name):
        """
        Uninstall an operator from a cluster
        """
        pass
