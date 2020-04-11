import logging
import pytest
import random
from time import sleep
from piqe_ocp_lib.api.resources import OcpProjects
from piqe_ocp_lib.api.resources.ocp_operators import OperatorhubPackages, CatalogSourceConfig, \
    Subscription, OperatorSource, OperatorGroup, ClusterServiceVersion
from piqe_ocp_lib.api.tasks.operator_ops import OperatorInstaller
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope='session')
def get_test_objects(get_kubeconfig):
    """
    Prepare the test artifacts as an object and pass it as
    a fixture.
    """
    class TestObjects:
        def __init__(self):
            self.op_hub_obj = OperatorhubPackages(kube_config_file=get_kubeconfig)
            self.csc_obj = CatalogSourceConfig(kube_config_file=get_kubeconfig)
            self.sub_obj = Subscription(kube_config_file=get_kubeconfig)
            self.og_obj = OperatorGroup(kube_config_file=get_kubeconfig)
            self.os_obj = OperatorSource(kube_config_file=get_kubeconfig)
            self.csv_obj = ClusterServiceVersion(kube_config_file=get_kubeconfig)
            self.project_obj = OcpProjects(kube_config_file=get_kubeconfig)
            self.oi_obj = OperatorInstaller(kube_config_file=get_kubeconfig)
            self.ocp_version = '.'.join(self.csc_obj.version)
    test_objs = TestObjects()
    return test_objs


@pytest.fixture(autouse=True)
def required_version(request, get_test_objects):
    """
    We create a custom marker called 'skip_if_not_version' and pass it
    the desired version of Openshift we want to test on as an argument.
    We look for that marker in request.node using get_closest_marker,
    if it's there, we check desired version against detected version
    that is obtained via the base class. If we don't have a match,
    we explicitly skip using pytest.skip()
    """
    skip_marker = request.node.get_closest_marker('skip_if_not_version')
    if not skip_marker:
        return
    else:
        desired_version = skip_marker.args[0]
    if desired_version != get_test_objects.ocp_version:
        logger.warning("The current test module requires version {}, "
                       "but version {} was detected".format(desired_version, get_test_objects.ocp_version))
        pytest.skip()


class TestOcpOperatorHub:

    def test_get_package_manifest_list(self, get_test_objects):
        # Simple check on the kind of the response object
        pkgs_obj = get_test_objects.op_hub_obj
        pkgs_resp_obj = pkgs_obj.get_package_manifest_list()
        assert pkgs_resp_obj.kind == 'PackageManifestList'

    def test_get_package_manifest(self, get_test_objects):
        # Check kind on response object and that metadata.name matches
        # the name given on creation
        pkg_obj = get_test_objects.op_hub_obj
        pkg_list = pkg_obj.get_package_manifest_list()
        rand_pkg = random.choice(pkg_list.items)
        pkg_details = pkg_obj.get_package_manifest(rand_pkg.metadata.name)
        assert pkg_details.kind == 'PackageManifest' and pkg_details.metadata.name == rand_pkg.metadata.name

    def test_get_package_channels_list(self, get_test_objects):
        # Check that the response object type is a list and that
        # the channels list has an install modes list.
        # Finally, there have to be exactly four distinct install modes
        pkg_obj = get_test_objects.op_hub_obj
        pkg_list = pkg_obj.get_package_manifest_list()
        rand_pkg = random.choice(pkg_list.items)
        channels_list = pkg_obj.get_package_channels_list(rand_pkg.metadata.name)
        assert isinstance(channels_list, list)
        for channel in channels_list:
            assert 'installModes' in channel['currentCSVDesc'].keys()
            assert len(channel['currentCSVDesc']['installModes']) == 4

    def test_get_package_allnamespaces_channel(self, get_test_objects):
        # We pick a random package and check wether it has a clusterwide channel
        # If it does, we check that the 4th object in the install modes list
        # is of type 'AllNamespaces' and that it is enabled
        pkg_obj = get_test_objects.op_hub_obj
        pkg_list = pkg_obj.get_package_manifest_list()
        rand_pkg = random.choice(pkg_list.items)
        logger.info("Package name is: {}".format(rand_pkg.metadata.name))
        cluster_wide_channel = pkg_obj.get_package_allnamespaces_channel(rand_pkg.metadata.name)
        if cluster_wide_channel:
            assert cluster_wide_channel['currentCSVDesc']['installModes'][3]['type'] == 'AllNamespaces'
            assert cluster_wide_channel['currentCSVDesc']['installModes'][3]['supported'] is True
        else:
            logger.info("The randomly picked package doesn't seem to have a clusterwide channel")

    def test_get_package_singlenamespace_channel(self, get_test_objects):
        # We pick a random package and check wether it has a singlenamespace channel
        # If it does, we check that the 2nd object in the install modes list
        # is of type 'SingleNamespace' and that it is supported
        pkg_obj = get_test_objects.op_hub_obj
        pkg_list = pkg_obj.get_package_manifest_list()
        rand_pkg = random.choice(pkg_list.items)
        logger.info("Package name is: {}".format(rand_pkg.metadata.name))
        single_namespace_channel = pkg_obj.get_package_singlenamespace_channel(rand_pkg.metadata.name)
        if single_namespace_channel:
            assert single_namespace_channel['currentCSVDesc']['installModes'][1]['type'] == 'SingleNamespace'
            assert single_namespace_channel['currentCSVDesc']['installModes'][1]['supported'] is True
        else:
            logger.warning("The randomly picked package doesn't seem to have a single namespace channel")


@pytest.mark.skip_if_not_version('4.1')
class TestCatalogSourceConfig:
    """
    CatalogSourceConfigs are supported in Openshift version 4.1. They are available
    in version 4.2 but not supported. The schema is also slightly changed. On this note
    CatalogSourceConfig objects will not be used as part version 4.2 testing. Instead,
    OperatorSource objects can be used instead, which work on both version 4.1 and 4.2.
    """
    def test_create_catalog_source_config(self, get_test_objects):
        # Create a test project that will contain the catalog source
        # config. We create a csc that enables the 'etcd' operator
        # then we check the kind of the response object as well as the
        # name given to the csc
        project_obj = get_test_objects.project_obj
        project_obj.create_a_project('test-project0')
        logger.info("Detected openshift version is: {}".format(get_test_objects.ocp_version))
        csc_obj = get_test_objects.csc_obj
        csc_resp_obj = csc_obj.create_catalog_source_config('test-csc',
                                                            ['etcd'],
                                                            target_namespace='test-project0')
        assert csc_resp_obj.kind == 'CatalogSourceConfig' and csc_resp_obj.metadata.name == 'test-csc'

    def test_label_catalog_source_config(self, get_test_objects):
        # We check the ability to label a catalog source config after it has
        # been created.
        # NOTE: often we hit a race condition and the csc object is not fully formed
        # by the time we try to label it, so we sleep to give it enough time to be ready.
        # This is a short term fix, the right way to address this is to add a watch/polling
        # method to the CatalogSourceConfig class
        # TODO: Replace sleep with watch/poll mechanism
        sleep(10)
        csc_obj = get_test_objects.csc_obj
        csc_resp_obj = csc_obj.label_catalog_source_config('test-csc', {'Owner': 'PIQE'})
        assert ('Owner', 'PIQE') in csc_resp_obj.metadata.labels.viewitems()
        assert 'etcd'

    def test_update_catalog_source_config_packages(self, get_test_objects):
        # Check that additions to the packages list is properly reflected
        # NOTE: often we hit a race condition and the csc object is not fully formed
        # by the time we try to update it, so we sleep to give it enough time to be ready.
        # This is a short term fix, the right way to address this is to add a watch/polling
        # method to the CatalogSourceConfig class
        # TODO: Replace sleep with watch/poll mechanism
        sleep(10)
        csc_obj = get_test_objects.csc_obj
        csc_resp_obj = csc_obj.update_catalog_source_config_packages('test-csc', ['nfd', 'datagrid'])
        assert any(s in csc_resp_obj.spec.packages for s in ['nfd', 'datagrid'])

    def test_get_catalog_source_config(self, get_test_objects):
        # Check kind and name correctness. Also check that all the packages we added
        # to the csc are present
        csc_obj = get_test_objects.csc_obj
        csc_resp_obj = csc_obj.get_catalog_source_config('test-csc')
        assert csc_resp_obj.kind == 'CatalogSourceConfig' and csc_resp_obj.metadata.name == 'test-csc'
        assert any(s in csc_resp_obj.spec.packages for s in ['etcd', 'nfd', 'datagrid'])

    def test_delete_catalog_source_config(self, get_test_objects):
        # Typically the response object is of type status, however for
        # this resource it is a csc obj. To check proper deletion we
        # init a response object to None, wetry to get the csc object
        # after we delete it. The try/expect catches the exception, so
        # the response object should still be None
        csc_obj = get_test_objects.csc_obj
        csc_obj.delete_catalog_source_config('test-csc')
        get_resp = None
        try:
            get_resp = csc_obj.get_catalog_source_config('test-csc')
        except ValueError:
            assert not get_resp
        get_test_objects.project_obj.delete_a_project('test-project0')


class TestOperatorSource:

    def test_create_operator_source(self, get_test_objects):
        # Create an operator source resource and check
        # kind and name for correctness
        spec_dict = {
            "displayName": "Copy of Red Hat Operators",
            "endpoint": "https://quay.io/cnr",
            "publisher": "Red Hat",
            "registryNamespace": "redhat-operators",
            "type": "appregistry"
        }
        os_obj = get_test_objects.os_obj
        os_resp_obj = os_obj.create_operator_source('test-os', spec_dict)
        assert os_resp_obj.kind == 'OperatorSource' and os_resp_obj.metadata.name == 'test-os'

    def test_get_operator_source(self, get_test_objects):
        # Get the operator source and check kind and name
        # for correctness
        os_obj = get_test_objects.os_obj
        os_resp_obj = os_obj.get_operator_source('test-os')
        assert os_resp_obj.kind == 'OperatorSource' and os_resp_obj.metadata.name == 'test-os'

    def test_delete_operator_source(self, get_test_objects):
        # Typically the response object is of type status, however for
        # this resource it is an operator source obj. To check proper deletion
        # we init a response object to None, wetry to get the csc object
        # after we delete it. The try/expect catches the exception, so
        # the response object should still be None
        os_obj = get_test_objects.os_obj
        os_obj.delete_operator_source('test-os')
        get_resp = None
        try:
            get_resp = os_obj.get_operator_source('test-os')
        except ValueError:
            assert not get_resp


class TestSubscription:
    """
    Creating a subscription resource requires a source
    In this test module we test subscriptions with catalog
    source configs as their source. This is only supported
    with Openshift version 4.1
    """
    def test_create_subscription(self, get_test_objects):
        # Create a subscription and check kind and name
        # for correctness
        get_test_objects.project_obj.create_a_project('test-project1')
        sub_resp_obj = get_test_objects.sub_obj.create_subscription('etcd',
                                                                    'SingleNamespace',
                                                                    'test-project1')
        assert sub_resp_obj.kind == 'Subscription' and sub_resp_obj.metadata.name == 'etcd'

    def test_get_subscription(self, get_test_objects):
        # Get the subscription and check kind and name
        # for correctness
        sub_resp_obj = get_test_objects.sub_obj.get_subscription('etcd', 'test-project1')
        assert sub_resp_obj.kind == 'Subscription' and sub_resp_obj.metadata.name == 'etcd'

    def test_delete_subscription(self, get_test_objects):
        # The response object for deleting a subscription is of type Status
        # so we check it has completed successfully
        sub_resp_obj = get_test_objects.sub_obj.delete_subscription('etcd', 'test-project1')
        assert sub_resp_obj.status == 'Success'
        get_test_objects.project_obj.delete_a_project('test-project1')


class TestOperatorGroup:

    def test_create_operator_group(self, get_test_objects):
        # Create an operator group and check kind and name
        # for correctness
        get_test_objects.project_obj.create_a_project('og-project')
        get_test_objects.project_obj.create_a_project('test-project2')
        og_resp_obj = get_test_objects.og_obj.create_operator_group('test-og', 'og-project', ['test-project2'])
        assert og_resp_obj.kind == 'OperatorGroup' and og_resp_obj.metadata.name == 'test-og'

    def test_get_operator_group(self, get_test_objects):
        # Get the operator group and check kind and name
        # for correctness. Also, check that the 'targetNamespace'
        # is set correctly
        og_resp_obj = get_test_objects.og_obj.get_operator_group('test-og', 'og-project')
        assert og_resp_obj.kind == 'OperatorGroup' and og_resp_obj.metadata.name == 'test-og'
        assert og_resp_obj.spec.targetNamespaces == ['test-project2']

    def test_delete_operator_group(self, get_test_objects):
        # The response object for deleting a subscription is of type Status
        # so we check it has completed successfully
        og_resp_obj = get_test_objects.og_obj.delete_operator_group('test-og', 'og-project')
        assert og_resp_obj.status == 'Success'
        get_test_objects.project_obj.delete_a_project('og-project')
        get_test_objects.project_obj.delete_a_project('test-project2')


class TestClusterServiceVersion:
    """
    In the end to end installation workflow of an operator in a cluster,
    a subscription has to be created in a namespace containing an operator
    group that is consistent with the install mode selected. This results
    in the creation of CSVs in all of the targeted namespaces. Subscriptions
    require a source. In this test module we use an operator source as a
    source for our subscription
    """

    @pytest.mark.skip(reason="Skip until MPQEENABLE-365 is resolved")
    def test_get_cluster_service_version(self, get_test_objects):
        # We create a target namespace and use 'openshift-marketplace'
        # which already contains an operator source by default. That saves
        # us the extra step of creating an operator source. We create a
        # subscription and sleep for 10 seconds before we try to perform a
        # get operation on it.
        # TODO: Replace sleep with watch/polling mechanism.
        # We obtain the CSV name from the subscription response object.
        # Finally we check kind and name for correctness and proceed with
        # cleaning up test artifacts.
        get_test_objects.project_obj.create_a_project('test-project3')
        # os_resp_obj = get_test_objects.os_obj.get_operator_source('community-operators')
        get_test_objects.og_obj.create_operator_group('test-og',
                                                      'openshift-marketplace',
                                                      ['test-project3'])
        get_test_objects.sub_obj.create_subscription('kong', 'SingleNamespace', 'openshift-marketplace')
        sleep(10)
        sub_resp_obj = get_test_objects.sub_obj.get_subscription('kong', 'openshift-marketplace')
        sleep(10)
        csv_name = sub_resp_obj.status.currentCSV
        csv_resp_obj = get_test_objects.csv_obj.get_cluster_service_version(csv_name, 'test-project3')
        sleep(20)
        assert csv_resp_obj.kind == 'ClusterServiceVersion' and csv_resp_obj.metadata.name == csv_name
        get_test_objects.og_obj.delete_operator_group('test-og', 'openshift-marketplace')
        get_test_objects.sub_obj.delete_subscription('kong', 'openshift-marketplace')
        get_test_objects.project_obj.delete_a_project('test-project3')


class TestInstallOperatorWorkflow:
    """
    A project with the name: 'test-' + operator_name + '-' + install_mode.lower() + '-og-sub-project'
    within the __create_og method in OperatorInstaller class.
    It gets automaticaly created to hold the subscription and operatorgroup objects
    Cleanup of this project will be handled automatically when the uninstall procedure of
    of an operator is implemented, and this test will be updated.
    """

    @pytest.mark.skip(reason="Skip until MPQEENABLE-356 is resolved")
    def test_add_operator_singlenamespace(self, get_test_objects):
        get_test_objects.project_obj.create_a_project('test-project4')
        get_test_objects.oi_obj.add_operator_to_cluster('amq-streams', target_namespaces=['test-project4'])
        csv_name = get_test_objects.op_hub_obj.get_package_singlenamespace_channel('amq-streams').currentCSV
        assert get_test_objects.csv_obj.is_cluster_service_version_present(csv_name, 'test-project4')
        # TODO: update when delete_operator_from_cluster is implemented
        get_test_objects.project_obj.delete_a_project('test-amq-streams-singlenamespace-og-sub-project')
        get_test_objects.project_obj.delete_a_project('test-project4')

    @pytest.mark.skip(reason="Skip until MPQEENABLE-356 is resolved")
    def test_add_operator_multinamespace(self, get_test_objects):
        get_test_objects.project_obj.create_a_project('test-project5')
        get_test_objects.project_obj.create_a_project('test-project6')
        get_test_objects.oi_obj.add_operator_to_cluster('amq-streams',
                                                        target_namespaces=['test-project5', 'test-project6'])
        csv_name = get_test_objects.op_hub_obj.get_package_multinamespace_channel('amq-streams').currentCSV
        assert get_test_objects.csv_obj.is_cluster_service_version_present(csv_name, 'test-project5')
        assert get_test_objects.csv_obj.is_cluster_service_version_present(csv_name, 'test-project6')
        # TODO: update when delete_operator_from_cluster is implemented
        get_test_objects.project_obj.delete_a_project('test-amq-streams-multinamespace-og-sub-project')
        get_test_objects.project_obj.delete_a_project('test-project5')
        get_test_objects.project_obj.delete_a_project('test-project6')

    @pytest.mark.skip(reason="Skip until MPQEENABLE-356 is resolved")
    def test_add_operator_clusterwide(self, get_test_objects):
        get_test_objects.project_obj.create_a_project('test-project7')
        get_test_objects.oi_obj.add_operator_to_cluster('amq-streams')
        csv_name = get_test_objects.op_hub_obj.get_package_allnamespaces_channel('amq-streams').currentCSV
        all_projects = get_test_objects.project_obj.get_all_projects()
        for project in all_projects.items:
            assert get_test_objects.csv_obj.is_cluster_service_version_present(csv_name, project.metadata.name)
        get_test_objects.project_obj.delete_a_project('test-amq-streams-allnamespaces-og-sub-project')
        get_test_objects.project_obj.delete_a_project('test-project7')
        # TODO: look into why the csv persits in openshift-operators project after cleaning
        # test artifacts
        get_test_objects.project_obj.delete_a_project('openshift-operators')

    @pytest.mark.skip(reason="Skip until MPQEENABLE-356 is resolved")
    def test_add_operator_using_operatorsource(self, get_test_objects):
        get_test_objects.project_obj.create_a_project('test-project8')
        operator_source = {
            "apiVersion": "operators.coreos.com/v1",
            "kind": "OperatorSource",
            "metadata": {
                "name": "yaks",
                "namespace": "openshift-marketplace"
            },
            "spec": {
                "type": "appregistry",
                "endpoint": "https://quay.io/cnr",
                "registryNamespace": "yaks",
                "displayName": "YAKS Operators",
                "publisher": "Red Hat"
            }
        }
        get_test_objects.oi_obj.add_operator_to_cluster('yaks', source=operator_source,
                                                        target_namespaces=['test-project8'])
        csv_name = get_test_objects.op_hub_obj.get_package_singlenamespace_channel('yaks').currentCSV
        assert get_test_objects.csv_obj.is_cluster_service_version_present(csv_name, 'test-project8')
        get_test_objects.project_obj.delete_a_project('test-yaks-singlenamespace-og-sub-project')
        get_test_objects.project_obj.delete_a_project('test-project8')
        get_test_objects.os_obj.delete_operator_source('yaks')
