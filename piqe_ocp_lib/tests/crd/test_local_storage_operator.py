import logging

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.crd.local_storage_operator import (
    LocalStorageOperator,
    LocalVolume,
    LocalVolumeDiscovery,
    LocalVolumeSet,
)
from piqe_ocp_lib.api.resources.ocp_operators import ClusterServiceVersion

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="session")
def get_test_objects(get_kubeconfig):
    """
    Prepare the test artifacts as an object and pass it as
    a fixture.
    """

    class TestObjects:
        def __init__(self):
            self.csv_obj = ClusterServiceVersion(kube_config_file=get_kubeconfig)
            self.lso = LocalStorageOperator(kube_config_file=get_kubeconfig)
            self.lv = LocalVolume(kube_config_file=get_kubeconfig)
            self.lvs = LocalVolumeSet(kube_config_file=get_kubeconfig)
            self.lvd = LocalVolumeDiscovery(kube_config_file=get_kubeconfig)

    test_objs = TestObjects()
    return test_objs

    @pytest.fixture(scope="module")
    def local_storage_operator(get_kubeconfig) -> LocalStorageOperator:
        return LocalStorageOperator(kube_config_file=get_kubeconfig)

    @pytest.fixture(scope="module")
    def local_volume(get_kubeconfig) -> LocalVolume:
        return LocalVolume(kube_config_file=get_kubeconfig)

    @pytest.fixture(scope="module")
    def local_volume_set(get_kubeconfig) -> LocalVolume:
        return LocalVolumeSet(kube_config_file=get_kubeconfig)

    @pytest.fixture(scope="module")
    def local_volume_discovery(get_kubeconfig) -> LocalVolume:
        return LocalVolumeDiscovery(kube_config_file=get_kubeconfig)


class TestLocalStorageOperator:
    lv_name = "testlvname"
    lvs_name = "testlvsname"
    lvd_name = "auto-discover-devices"

    def test_create_local_volume(self, get_test_objects):
        api_response = get_test_objects.lv.create_local_volume(
            local_volume_name=TestLocalStorageOperator.lv_name, storage_class_name="teststoragevlass"
        )
        assert api_response.kind == "LocalVolume"
        assert api_response.metadata.name == TestLocalStorageOperator.lv_name

    def test_get_local_volume(self, get_test_objects):
        api_response = get_test_objects.lv.get_local_volume("openshift-local-storage", TestLocalStorageOperator.lv_name)
        assert api_response.kind == "LocalVolume"
        assert api_response.metadata.name == TestLocalStorageOperator.lv_name

    def test_watch_local_volume(self, get_test_objects):
        assert (
            get_test_objects.lv.watch_local_volume(
                "openshift-local-storage", TestLocalStorageOperator.lv_name, timeout=120
            )
            is not False
        )

    def test_delete_local_volume(self, get_test_objects):
        assert get_test_objects.lv.delete_local_volume(TestLocalStorageOperator.lv_name) is not None

    def test_create_local_volume_set(self, get_test_objects):
        api_response = get_test_objects.lvs.create_local_volume_set(
            name=TestLocalStorageOperator.lvs_name,
            storageClassName="teststoragelvsclass",
            deviceTypes=["disk", "part"],
            volumeMode="Block",
        )

    def test_get_local_volume_set(self, get_test_objects):
        api_response = get_test_objects.lvs.get_local_volume_set(
            "openshift-local-storage", TestLocalStorageOperator.lvs_name
        )
        assert api_response.kind == "LocalVolumeSet"

    def test_watch_local_volume_set(self, get_test_objects):
        assert (
            get_test_objects.lvs.watch_local_volume_set(
                "openshift-local-storage", TestLocalStorageOperator.lvs_name, timeout=120
            )
            is not False
        )

    def test_delete_local_volume_set(self, get_test_objects):
        assert get_test_objects.lvs.delete_local_volume_set(TestLocalStorageOperator.lvs_name) is not None

    def test_create_local_volume_discovery(self, get_test_objects):
        api_response = get_test_objects.lvd.create_local_volume_discovery()

    def test_get_local_volume_discovery(self, get_test_objects):
        api_response = get_test_objects.lvd.get_local_volume_discovery(
            "openshift-local-storage", TestLocalStorageOperator.lvd_name
        )
        assert api_response.kind == "LocalVolumeDiscovery"

    def test_watch_local_volume_discovery(self, get_test_objects):
        assert (
            get_test_objects.lvd.watch_local_volume_discovery(
                "openshift-local-storage", TestLocalStorageOperator.lvd_name, timeout=120
            )
            is not False
        )

    def test_delete_local_volume_discovery(self, get_test_objects):
        assert get_test_objects.lvd.delete_local_volume_discovery(TestLocalStorageOperator.lvd_name) is not None
