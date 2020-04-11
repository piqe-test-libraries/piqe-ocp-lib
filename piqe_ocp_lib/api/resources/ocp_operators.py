from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from kubernetes.client.rest import ApiException
import logging
from piqe_ocp_lib import __loggername__
from time import sleep

logger = logging.getLogger(__loggername__)


class OperatorhubPackages(OcpBase):
    """
    A class that offers the capability to query and inspect operator package manifests
    Available from the OperatorHub. The Hub provides a catalog of operators from different
    sources.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(OperatorhubPackages, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'packages.operators.coreos.com/v1'
        self.kind = 'PackageManifest'
        self.package_manifest_obj = self.dyn_client.resources.get(api_version=self.api_version,
                                                                  kind=self.kind)

    def get_package_manifest_list(self, catalog=None):
        """
        A method that retrieves the entire list of package manifest objects
        visible by the OperatorHub regardless of the source
        :param catalog: The name of the catalog with which we want to filter results
                        by default, there are three different catalogs available:
                        'Red Hat Operators'
                        'Certified Operators'
                        'Community Operators'
        :return: a list of PackageManifest objects when successfule, otherwise it
                 returns an empty list.
        TODO: Instead of filtering by catalog, is it better to filter by
              spec.catalogSource?
        """
        packages_obj_list = []
        try:
            if not catalog:
                packages_obj_list = self.package_manifest_obj.get()
            else:
                packages_obj_list = self.package_manifest_obj.get(label_selector='catalog={}'.format(catalog))
        except ApiException as e:
            logger.exception("Exception when calling method get_package_manifest_list: %s\n" % e)
        return packages_obj_list

    def get_package_manifest(self, package_name):
        """
        A method that gets the manifest details on a specific operator manifest file
        :param package_name: The name or the operator package manifest object we want
                             to obtain.
        :return: a PackageManifest object if present, otherwise it returns None.
        """
        package_obj = None
        try:
            package_obj = self.package_manifest_obj.get(field_selector='metadata.name={}'.format(package_name))
        except ApiException as e:
            logger.exception("Exception when calling method get_package_manifest: %s\n" % e)
        if package_obj and len(package_obj.items) == 1:
            return package_obj.items[0]
        else:
            return package_obj

    def watch_package_manifest_present(self, package_name, timeout=30):
        """
        Watch doesn't seem to be supported of resource type PackageManifest
        so we have implement it ourselves.
        :param package_name: (required | str) name of the package to be watched
        :param timeout: (optional | int) maximum time (in seconds) to watch a
                        package before erroring out. Defaults to 30 seconds.
        """
        counter = 0
        while counter < timeout:
            if not self.get_package_manifest(package_name):
                counter += 5
                sleep(5)
                logger.info("Waiting for package {} to be available in OperatorHub".format(package_name))
            else:
                logger.info("Package {} was detected in OperatorHub".format(package_name))
                return True
        return False

    def get_package_channels_list(self, package_name):
        """
        A method that returns a list of available subscription channels for a particular
        package. Different channels maps to one or more install modes.
        :param package_name: The name of the operator package for which we want to obtain
                             the supported channels list.
        :return: A list of subscription channels.
        """
        channels_list = []
        try:
            channels_list = self.get_package_manifest(package_name=package_name).status.channels
        except ApiException as e:
            logger.exception("Exception when calling method get_package_channels_list: %s\n" % e)
        return channels_list

    def get_package_allnamespaces_channel(self, package_name):
        """
        A method that specifically retrieves the name of a package's channel name
        that allows the user to enable the operator across all namespaces/projects
        of the entire cluster.
        :param package_name: The name of the operator package for which we want to
                             obtain the clusterwide channel name.
        :return: The name of the clusterwide channel, if availabele, otherwise
                 the method returns None.
        """
        channels_list = self.get_package_channels_list(package_name)
        clusterwide_channels = []
        for channel in channels_list:
            install_modes = channel.currentCSVDesc.installModes
            for im in install_modes:
                if im.type == 'AllNamespaces' and im.supported is True:
                    clusterwide_channels.append(channel)
        if len(clusterwide_channels) != 0:
            return clusterwide_channels[-1]
        else:
            logger.error("A clusterwide channel was not found for package: {}".format(package_name))
        return None

    def get_package_multinamespace_channel(self, package_name):
        """
        A method that specifically retrieves the name of a package's channel name
        that allows the user to enable the operator in multiple namespaces/projects.
        :param package_name: The name of the operator package for which we want to
                             obtain the multinamespace channel name.
        :return: The name of the multinamespace channel, if availabele, otherwise
                 the method returns None.
        """
        channels_list = self.get_package_channels_list(package_name)
        multinamespace_channels = []
        for channel in channels_list:
            install_modes = channel.currentCSVDesc.installModes
            for im in install_modes:
                if im.type == 'MultiNamespace' and im.supported is True:
                    multinamespace_channels.append(channel)
        if len(multinamespace_channels) != 0:
            return multinamespace_channels[-1]
        else:
            logger.error("A MultiNamespace channel was not found for package: {}".format(package_name))
        return None

    def get_package_singlenamespace_channel(self, package_name):
        """
        A method that specifically retrieves the name of a package's channel name
        that allows the user to enable the operator in a single namespaces/project.
        :param package_name: The name of the operator package for which we want to
                             obtain the single namespace channel name.
        :return: The name of the single namespace channel, if availabele, otherwise
                 the method returns None.
        """
        channels_list = self.get_package_channels_list(package_name)
        singlenamespace_channels = []
        for channel in channels_list:
            install_modes = channel.currentCSVDesc.installModes
            for im in install_modes:
                if im.type == 'SingleNamespace' and im.supported is True:
                    singlenamespace_channels.append(channel)
        if len(singlenamespace_channels) != 0:
            return singlenamespace_channels[-1]
        else:
            logger.error("A SingleNamespace channel was not found for package: {}".format(package_name))
        return None

    def get_package_ownnamespace_channel(self, package_name):
        """
        A method that specifically retrieves the name of a package's channel name
        that allows the user to enable the operator in a single namespaces/project.
        :param package_name: The name of the operator package for which we want to
                             obtain the single namespace channel name.
        :return: The name of the single namespace channel, if availabele, otherwise
                 the method returns None.
        """
        channels_list = self.get_package_channels_list(package_name)
        ownnamespace_channels = []
        for channel in channels_list:
            install_modes = channel.currentCSVDesc.installModes
            for im in install_modes:
                if im.type == 'OwnNamespace' and im.supported is True:
                    ownnamespace_channels.append(channel)
        if len(ownnamespace_channels) != 0:
            return ownnamespace_channels[-1]
        else:
            logger.error("A OwnNamespace channel was not found for package: {}".format(package_name))
        return None


class CatalogSourceConfig(OcpBase):
    """
    A class that provides a user the ability to create catalog source config objects whcih then can be used
    to create subscriptions to a custom list or operators available throught the operator hub.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(CatalogSourceConfig, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'operators.coreos.com/v1'
        self.kind = 'CatalogSourceConfig'
        self.catalog_source_config_obj = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_catalog_source_config(self, csc_name=None,
                                     package_list=None,
                                     target_namespace='openshift-operators',
                                     body=None,
                                     cs_display_name=None,
                                     cs_publisher=None,
                                     labels_dict=None):
        """
        A method to create a CatalogSourceConfig object as described in section 2.4.1.2
        of the downstream docs (version 4.1)
        :param csc_name: (required | str) The name of the CatalogSourceConfig object to be created.
        :param package_list: (required | list of strings) A list of names of operators that the
                             user wants to install.
        :param target_namespace: (required | list) By default, we will always create a CatalogSourceConfig
                                 object in the 'openshfit-marketplace' namespace. When that is done, an object
                                 of type CatalogSource is automatically created in target_namespace.
        :param body: the request body in dict format. If specified, other optional params will be ignored.
        :param cs_display_name: (optional | str) The display nanme for you CatalogSourceConfig
        :param cs_publisher: (optional | str) The publisher name for you CatalogSourceConfig
        :param labels_dict: (optional | dict) The key/val labels to be applied to the CatalogSourceConfig
        :return: An Api response object of type CatalogSourceConfig
        NOTE: *** This class will always create CatalogSourceConfig objects in the 'openshift-marketplace
              namespace ***
        """
        if body:
            csc_body = body
        else:
            if not isinstance(package_list, list):
                logger.exception("The parameter package_list must be of type list")
                raise ValueError("The parameter package_list must be of type list")
            else:
                csc_body = {
                    "apiVersion": self.api_version,
                    "kind": self.kind,
                    "metadata": {
                        "name": "{}".format(csc_name),
                        "namespace": "openshift-marketplace",
                    },
                    "spec": {
                        "csDisplayName": "PIQE Test Operators",
                        "csPublisher": "PIQE",
                        "targetNamespace": target_namespace,
                        "packages": ','.join(package_list)
                    }
                }
                # Add optional params to the obj body
                if cs_display_name:
                    csc_body['spec']['csDisplayName'] = cs_display_name
                if cs_publisher:
                    csc_body['spec']['csPublisher'] = cs_publisher
                if labels_dict:
                    csc_body['metadata']['labels'] = labels_dict
        api_response = None
        try:
            api_response = self.catalog_source_config_obj.create(body=csc_body)
        except ApiException as e:
            logger.exception("Exception when calling method create_catalog_source_config: %s\n" % e)
        return api_response

    def delete_catalog_source_config(self, csc_name):
        """
        A method to delete a catalog source config resource by name.
        :param csc_name: (required | str) The name of the csc we want to delete
        :return: A CatalogSourceConfig object (NOTE: is it a bug? typically it's an object
                 of type 'Status')
        """
        # NOTE: When a catalog source config is created in the openshift-marketplace
        # and object of type 'CatalogSource' get automatically created in 'targetNamespace'
        # as soon as the csc is deleted, the associated catalog source gets automatically
        # deleted as well.
        api_response = None
        try:
            api_response = self.catalog_source_config_obj.delete(name=csc_name, namespace='openshift-marketplace')
        except ApiException as e:
            logger.exception("Exception when calling method delete_catalog_source_config: %s\n" % e)
        return api_response

    def label_catalog_source_config(self, csc_name, labels_dict):
        """
        A method to lable a CatalogSourceconfig object
        :param csc_name: (required | str) The CatalogSourceConfig obj to be labeled
        :param labels_dict: (required | dict) The key/val labels to be applied to the CatalogSourceConfig
        :param return: A CatalogSourceConfig object
        NOTE: Typically we would use the dynamic client's patch functionality to achieve this.
        However, patch is not supported on non native kubernetes resources.
        """
        api_response = None
        csc_body = self.get_catalog_source_config(csc_name)
        csc_body.metadata.update({"labels": labels_dict})
        try:
            api_response = self.catalog_source_config_obj.apply(body=csc_body)
        except ApiException as e:
            logger.exception("Exception when calling method label_catalog_source_config: %s\n" % e)
        return api_response

    def get_catalog_source_config(self, csc_name):
        """
        A method that retrieves a CatalogSourceConfig object by name
        :param csc_name: (required | str) The name of the csc we want to retrieve
        :param return: A CatalogSourceConfig object
        """
        api_response = None
        try:
            api_response = self.catalog_source_config_obj.get(name=csc_name, namespace='openshift-marketplace')
        except ApiException as e:
            logger.exception("Exception when calling method get_catalog_source_config: %s\n" % e)
        return api_response

    def update_catalog_source_config_packages(self, csc_name, package_list):
        """
        A method that updates the list of supported packages by a csc
        :param csc_name: (required | str) The name of the csc we want to update
        :param package_list: (required | list) The list of package names that we want to update
        :param return: A CatalogSourceConfig object
        """
        if not isinstance(package_list, list):
            logger.exception("The parameter package_list must be of type list")
            raise ValueError("The parameter package_list must be of type list")
        api_response = None
        csc_body = self.get_catalog_source_config(csc_name)
        current_packages = csc_body.spec.packages
        updated_packages = current_packages + ',' + ','.join(package_list)
        csc_body.spec.update({"packages": updated_packages})
        try:
            api_response = self.catalog_source_config_obj.apply(body=csc_body)
        except ApiException as e:
            logger.exception("Exception when calling method update_catalog_source_config_packages: %s\n" % e)
        return api_response


class OperatorSource(OcpBase):
    """
    A class that provides a user the ability to create OperatorSource objects whcih then can be used
    to create subscriptions to packages available through that source.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(OperatorSource, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'operators.coreos.com/v1'
        self.kind = 'OperatorSource'
        self.operator_source_obj = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        # self.catalog_source_obj = CatalogSource(kube_config_file=kube_config_file)

    def create_operator_source(self, os_name=None, spec_dict=None, body=None, namespace='openshift-marketplace'):
        """
        A method to create a resource of type OperatorSource. This is typically used when an operator
        package manifest is available through some non-standard sources. This allows for the package to be
        accessible from the OperatorHub.
        :param os_name: (required | str) The operator source name
        :param spec_dict: (required | dict) The spec object contains as a minimum five keys:
                          type: The type of registry containing this source, typically appregistry
                          endpoint: The address of the registry, typycally https://quay.io/cnr
                          registryNamespace: The name of the namespace containing the the package in the registry.
                          displayName: The name that will be shown as 'catalog' or 'catalogSource' when added to
                                       the operatorhub.
                          publisher: Name of the publisher of this source.
                          TODO: pass these variables as a combination of required and optional params as opposed
                                to a dictionary to this method?
        :param return: An object of type OperatorSource
        """
        if body:
            os_body = body
        else:
            os_body = {
                "apiVersion": self.api_version,
                "kind": self.kind,
                "metadata": {
                    "name": os_name,
                    "namespace": namespace
                },
                "spec": spec_dict
            }
        api_response = None
        try:
            api_response = self.operator_source_obj.create(body=os_body)
        except ApiException as e:
            logger.exception("Exception when calling method create_operator_source: %s\n" % e)
        return api_response

    def get_operator_source(self, os_name, namespace='openshift-marketplace'):
        """
        A method that retrieves an operator source by name from a namespace, which by default,
        will be 'openshift-marketplace'
        :param os_name: (required | str) The name of the operator source to be created
        :param namespace: (optional | str) The name of the namespace where the operator
                           source should be created. Defaults to 'openshift-marketplace'
        :param return: An object of type OperatorSource
        """
        api_response = None
        try:
            api_response = self.operator_source_obj.get(name=os_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method get_operator_source: %s\n" % e)
        return api_response

    def delete_operator_source(self, os_name, namespace='openshift-marketplace'):
        """
        A method to delete an operator source by name in a namespace, which by default, will
        be 'openshift-marketplace'
        :param os_name: (required | str) The name of the operator source to be deleted
        :param namespace: (optional | str) The name of the namespace where the operator
                          source obejec to be deleted resides.
        """
        api_response = None
        try:
            api_response = self.operator_source_obj.delete(name=os_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method create_operator_source: %s\n" % e)
        return api_response


class CatalogSource(OcpBase):
    """
    A class that provides a user the ability to verify the presence of
    CatalogSource objects.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file):
        super(CatalogSource, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'operators.coreos.com/v1alpha1'
        self.kind = 'CatalogSource'
        self.catalog_source_obj = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_catalog_source(self, cs_name, namespace='openshift-marketplace'):
        """
        A method that retrieves a catalog source by name from a namespace, which by default,
        will be 'openshift-marketplace'
        :param cs_name: (required | str) The name of the catalog source to be retrieved
        :param namespace: (optional | str) The name of the namespace where the catalog
                           source is expected to be. Defaults to 'openshift-marketplace'
        :param return: An object of type CatalogSource
        """
        api_response = None
        try:
            # We can hard code namespace because all catalogsources will go in the
            # openshift-marketplace namespace. NOTE: if that were ever to change,
            # we'll need to parameterize the namespace argument.
            api_response = self.catalog_source_obj.get(name=cs_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method get_catalog_source: %s\n" % e)
        return api_response

    def get_all_catalog_sources(self):
        """
        A method that retrieves all catalog sources in an openshift cluster.
        :param return: An object of type CatalogSourceList
        """
        api_response = None
        try:
            api_response = self.catalog_source_obj.get()
        except ApiException as e:
            logger.exception("Exception when calling method get_all_catalog_sources: %s\n" % e)
        return api_response

    def is_catalog_source_present(self, cs_name, namespace='openshift-marketplace', timeout=30):
        """
        A method that verifies that a catalog source was created in a namespace. By default it
        will be 'openshift-marketplace'
        :param cs_name: (required | str) The name of the catalog source to be retrieved
        :param namespace: (optional | str) The name of the namespace where the catalog
                           source is expected to be. Defaults to 'openshift-marketplace'
        :param timeout: (optional | int) The amount of time in seconds we expect the watch
                        to be completed.
        :param return: (bool) A boolean value to indicate whether a catalog source is
                       present or not.
        """
        field_selector = "metadata.name={}".format(cs_name)
        for event in self.catalog_source_obj.watch(namespace=namespace, field_selector=field_selector, timeout=timeout):
            if event['object'] and event['object']['metadata']['name'] == cs_name:
                logger.info("CatalogSource {} in namescpace {} was found".format(cs_name, namespace))
                return True
        logger.warning("CatalogSource {} in namespace {} was not detected within a timeout interval"
                       " of {} seconds".format(cs_name, namespace, timeout))
        return False


class Subscription(OcpBase):
    """
    A class that provides a user the ability to create a subscription. A subscription is tied to
    a source, such as a catalogsourceconfig or operatorsource. Creating a subscription automatically
    creates cluster service versions (csv) resources in a targeted set of projects/namespaces where
    they will provide the metadate necessary for creating the custom resource definitions (CRD)
    for creating operator based apps.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(Subscription, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'operators.coreos.com/v1alpha1'
        self.kind = 'Subscription'
        self.subscription_obj = self.dyn_client.resources.get(api_version=self.api_version,
                                                              kind=self.kind)
        self.csc_obj = CatalogSourceConfig(kube_config_file=kube_config_file)
        self.package_manifest_obj = OperatorhubPackages(kube_config_file=kube_config_file)
        self.catalog_source_obj = CatalogSource(kube_config_file=kube_config_file)

    def create_subscription(self, operator_name, install_mode, namespace):
        """
        A method to create a subscription object in a namespace. NOTE: the namespace you pick must have an
        OperatorGroup that matches the InstallMode (either AllNamespaces or SingleNamespace modes)
        :param operator_name: (required | str) The name of the operator/package that you want to subscribe to.
        :param source_obj: (required | str) Either a CatalogSourceConfig object (OCPv4.1) or OperatorSource
                           object (OCPv4.1/4.2). Use either the get_operator_source method in the
                           OperatorSource calss or the get_catalog_source_config method in the
                           CatalogSourceConfig class to obtain this object.
        :param install_mode: (required | str) The install mode type for the operator. Currently two
                             out of the four install modes are supported: 'singleNamespace' or 'AllNamespaces'
        :param return: An object of type Subscription
        """
        # Based on the install mode chosen, we then need to fetch the corresponding subscription channel name
        # available in the package manifest for this operator.
        if install_mode == 'SingleNamespace':
            channel = self.package_manifest_obj.get_package_singlenamespace_channel(operator_name)
        elif install_mode == 'AllNamespaces':
            channel = self.package_manifest_obj.get_package_allnamespaces_channel(operator_name)
        elif install_mode == 'MultiNamespace':
            channel = self.package_manifest_obj.get_package_multinamespace_channel(operator_name)
        elif install_mode == 'OwnNamespace':
            channel = self.package_manifest_obj.get_package_ownnamespace_channel(operator_name)
        else:
            channel_error_msg = "Unrecognized or unsupported install mode provided"
            logger.exception(channel_error_msg)
            raise ValueError(channel_error_msg)
        # We get the CatalogSource name directly from the packagemanifest object
        # we then use that fetch the CatalogSource object in order to obtain its
        # namespace. NOTE: CatalogSources are typically in 'openshift-marketplace'
        # but it is also possible to create them in a different namespace in the
        # when using catalog source configs (see targetNamespace), so we shouldn't
        # hard code sourceNamespace to be 'openshift-marketplace'
        operator_pkg = self.package_manifest_obj.get_package_manifest(operator_name)
        cs_name = operator_pkg.status.catalogSource
        catalog_source = self.catalog_source_obj.get_catalog_source(cs_name)
        cs_namespace = catalog_source.metadata.namespace
        # From the subscription body
        subscription_body = {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": {
                "name": operator_name,
                "namespace": namespace
            },
            "spec": {
                "channel": channel.name,
                "installPlanApproval": "Automatic",
                "name": operator_name,
                "source": cs_name,
                "sourceNamespace": cs_namespace
            }
        }
        try:
            api_response = self.subscription_obj.apply(body=subscription_body)
        except ApiException as e:
            logger.exception("Exception when calling method create_subscription: %s\n" % e)
        return api_response

    def get_subscription(self, operator_name, namespace):
        """
        A method to get a subscription by name from a namespace
        :param operator_name: (required | str) Subscriptions have a one to one mapping to any one
                              operator, so the subscription name is the operator name
        :param namespace: (required | str) The namespace where the subscription is created
        :param return: A Subscription object
        """
        try:
            api_response = self.subscription_obj.get(name=operator_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method get_subscription: %s\n" % e)
        return api_response

    def delete_subscription(self, operator_name, namespace):
        """
        A method to delete a subscription by name from a namespace
        :param operator_name: (required | str) Subscriptions have a one to one mapping to any one
                              operator, so the subscription name is the operator name
        :param namespace: (required | str) The namespace from where the subscription is to be deleted
        :param return: A Subscription object
        """
        try:
            api_response = self.subscription_obj.delete(name=operator_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method delete_subscription: %s\n" % e)
        return api_response

    def watch_subscription_ready(self, operator_name, namespace, timeout):
        logger.info("Watching %s subscription for readiness" % operator_name)
        is_operator_ready = False
        field_selector = "metadata.name={}".format(operator_name)
        for event in self.subscription_obj.watch(namespace=namespace, field_selector=field_selector, timeout=timeout):
            for condition in event['object']['status']['conditions']:
                if condition["message"] == "all available catalogsources are healthy":
                    logger.info("Operator %s installed successfully", operator_name)
                    is_operator_ready = True
                    return is_operator_ready
        logger.error("Operator %s failed", operator_name)
        return is_operator_ready


class OperatorGroup(OcpBase):
    """
    A class that provides a user the ability to create an OperatorGroup. It provides
    multitenant configuration to OLM installed Operators. An OperatorGroup selects a set
    of target namespaces in which to generate required CSV's necessary for deploying
    instances of the CRDs.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(OperatorGroup, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'operators.coreos.com/v1'
        self.kind = 'OperatorGroup'
        self.operator_group_obj = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_operator_group(self, og_name, namespace, target_namespaces=[]):
        """
        A method to create an OperatorGroup object. If 'spec' is left out, it means that by default
        this operator group will target all namespaces for deployment. Otherwise, spec will contain
        a key called 'targetNamespaces' which will hold a list of namespaces targeted for deployment.
        NOTE: 'targetNamespaces' has to be consistent with the subscription install mode. Meaning,
        if the subscription install mode is 'SingleNamespace', then 'targetNamespace' in the operator
        group has to be one namespace. In case of a 'AllNamespaces' install mode, then spec in the
        operator group should be left out. Finally, there can be no more than one operator group
        per namespace.
        :param og_name: (required | str) The name of the operator group to be created
        :param namespace: (required | str) The namespace where the operator group
                          is to be created.
        :param target_namespaces:
        """
        # Verify that if target_namespaces default is overriden, it is of type list.
        if not isinstance(target_namespaces, list):
            err_msg = "'target_namespaces' argument must be provided in list format"
            logger.exception(err_msg)
            raise ValueError(err_msg)
        # TODO: Do further investigation to determine how to use kubernetes models
        # to build the bodies instead of defining them as dictionaries
        og_body = {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": {
                "name": og_name,
                "namespace": namespace
            }
        }
        # If target_namespaces is not the default [], added to the body as part of 'spec'
        if target_namespaces:
            og_body.update({"spec": {"targetNamespaces": target_namespaces}})
        try:
            api_response = self.operator_group_obj.apply(body=og_body)
        except ApiException as e:
            logger.exception("Exception when calling method create_operator_group: %s\n" % e)
        return api_response

    def get_operator_group(self, og_name, namespace):
        """
        A method to get an operator group by name from a namespace
        :param og_name: (requrired | str) The name of the operator group
        :param namespace: (required | str) The name of the namespace containing the
                          operator group
        :param return: An object of type OperatorGroup
        """
        try:
            api_response = self.operator_group_obj.get(name=og_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method get_operator_group: %s\n" % e)
        return api_response

    def delete_operator_group(self, og_name, namespace):
        """
        A method to get an operator group by name from a namespace
        :param og_name: (requrired | str) The name of the operator group to be deleted
        :param namespace: (required | str) The name of the namespace containing the
                          operator group to be deleted
        :param return: An object of type OperatorGroup
        """
        try:
            api_response = self.operator_group_obj.delete(name=og_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method delete_operator_group: %s\n" % e)
        return api_response


class ClusterServiceVersion(OcpBase):
    """
    A class that provides a user the ability to get a ClusterServiceVersion object.
    CSVs get created automatically when a valid subscription object is created. CSV
    is a manifest created from the Operator metadata that assists the Operator
    Lifecycle Manager (OLM) in running the Operator in a cluster. It is the metadata
    that accompanies an operator and contains technical information needed to run
    the Operator.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """
    def __init__(self, kube_config_file=None):
        super(ClusterServiceVersion, self).__init__(kube_config_file=kube_config_file)
        self.api_version = 'operators.coreos.com/v1alpha1'
        self.kind = 'ClusterServiceVersion'
        self.csv_obj = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_cluster_service_version(self, csv_name, namespace):
        """
        A method that gets a CSV by name from a namespace.
        :param csv_name: (required | str) The name of the CSV to be obtained. When a CSV is
                         generated after creating a Subscription object, the CSV name can be
                         found in the subscription response object (use get_subscription method
                         in the Subscription class) under status.currentCSV. This typically maps
                         to the channel name that matches the install mode in the package manifest
                         object.
        :param namespace: The name of the namespace containing the CSV
        :param return: A ClusterServiceVersion object
        """
        try:
            api_response = self.csv_obj.get(name=csv_name, namespace=namespace)
        except ApiException as e:
            logger.exception("Exception when calling method get_cluster_service_version: %s\n" % e)
        return api_response

    def is_cluster_service_version_present(self, csv_name, namespace, timeout=30):
        """
        A method that verifies that a cluster service version was created in a namespace.
        :param cs_name: (required | str) The name of the cluster service version to be retrieved
        :param namespace: (required | str) The name of the namespace where the cluster
                           service version is expected to be.
        :param timeout: (optional | int) The amount of time in seconds we expect the watch
                        to be completed.
        :param return: (bool) A boolean value to indicate whether a catalog source is
                       present or not.
        """
        field_selector = "metadata.name={}".format(csv_name)
        for event in self.csv_obj.watch(namespace=namespace, field_selector=field_selector, timeout=timeout):
            if event['object'] and event['object']['metadata']['name'] == csv_name:
                logger.info("ClusterServiceVersion {} in namescpace {} was found".format(csv_name, namespace))
                return True
        logger.warning("ClusterServiceVersion {} in namespace {} was not detected within a timeout interval"
                       " of {} seconds".format(csv_name, namespace, timeout))
        return False
