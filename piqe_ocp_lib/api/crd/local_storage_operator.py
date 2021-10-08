import logging
from time import time
from typing import Optional

from kubernetes.client.rest import ApiException
from openshift.dynamic.resource import ResourceInstance

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from piqe_ocp_lib.api.resources.ocp_operators import ClusterServiceVersion
from piqe_ocp_lib.api.tasks.operator_ops import OperatorInstaller

logger = logging.getLogger(__loggername__)


class LocalStorageOperator(OcpBase):
    """
    LocalStorageOperator Class extends OcpBase
    related to local storage operator
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.oi_obj = OperatorInstaller()
        self.check_operator_install = self.oi_obj.is_operator_installed("local-storage-operator")
        if self.check_operator_install is False:
            self.oi_obj.add_operator_to_cluster(operator_name="local-storage-operator")
            logger.info("local-storage-operator successfully installed")
        else:
            self.operator_version = self.oi_obj.get_version_of_operator("local-storage-operator")
            self.channel = self.oi_obj.get_channel_of_operator("local-storage-operator")


class LocalVolume(LocalStorageOperator):
    """
    LocalVolume Class extends LocalStorageOperator
    related to local volume
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "local.storage.openshift.io/v1"
        self.kind = "LocalVolume"
        self.lv = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_local_volume(
        self, local_volume_name, storage_class_name, fsType=None, volumeMode=None
    ) -> Optional[ResourceInstance]:
        """
        create local volume
        :param local_volume_name:(required) name  of the local volume

        :return api response
        """
        if self.operator_version is not None and self.channel is not None and self.check_operator_install is True:
            csv = ClusterServiceVersion()
            csv_obj = csv.get_cluster_service_version(
                "local-storage-operator." + self.operator_version, "openshift-local-storage"
            )
            crd = csv_obj.metadata.annotations["alm-examples"]
            for i in range(0, len(eval(crd))):
                if "'kind': 'LocalVolume', 'metadata'" in str(eval(crd)[i]):
                    target_item = i
            body = eval(crd)[target_item]
            if fsType is None and volumeMode is None:
                body["metadata"]["name"] = local_volume_name
                body["spec"]["storageClassDevices"][0]["storageClassName"] = storage_class_name
            else:
                body["metadata"]["name"] = local_volume_name
                body["spec"]["storageClassDevices"][0]["storageClassName"] = storage_class_name
                body = ["spec"]["storageClassDevices"][0]["fsType"] = fsType
                body = ["spec"]["storageClassDevices"][0]["volumeMode"] = volumeMode
            api_response = None
            try:
                api_response = self.lv.create(namespace="openshift-local-storage", body=body)
            except ApiException as e:
                logger.exception(f"Exception while creating Local Volume : {e}\n")
        else:
            logger.info("local storage operator is not installed")
        return api_response

    def get_local_volume(self, namespace: str, local_volume_name: str) -> Optional[ResourceInstance]:
        """
        get local volume
        param namespace: namespace of the local volume
        param local_volume_name: name of the local volume
        return: api response
        """
        api_response = None
        try:
            api_response = self.lv.get(namespace=namespace, name=local_volume_name)
        except ApiException as e:
            logger.exception(f"Exception while creating Local Volume : {e}\n")
        return api_response

    def watch_local_volume(self, namespace: str, local_volume_name: str, timeout: int) -> bool:
        """
        watch local volume
        param namespace: namespace of the local volume
        param local_volume_name: name of the local volume
        timeout: seconds for check
        return: is local volume ready (True | FALSE)
        """
        end = time() + timeout
        while time() < end:
            api_response = self.get_local_volume(namespace=namespace, local_volume_name=local_volume_name)
            if api_response.status is not None:
                break
            else:
                logger.info(f"local volume {local_volume_name} status is present, waiting for ready state")
                continue
        if len(api_response.status.conditions) != 0:
            is_local_volume_ready = False
            field_selector = f"metadata.name={local_volume_name}"
            for event in self.lv.watch(
                namespace="openshift-local-storage", field_selector=field_selector, timeout=timeout
            ):
                for condition in event["object"]["status"]["conditions"]:
                    if condition["message"] == "Ready":
                        logger.info(f"local volume {local_volume_name} status is ready")
                        is_local_volume_ready = True
                        return is_local_volume_ready
                    else:
                        logger.info(f"local volume{local_volume_name} is waiting for ready state")
        else:
            logger.error(f"status for {local_volume_name} volume is not present")
        return is_local_volume_ready

    def delete_local_volume(self, local_volume_name: str) -> Optional[ResourceInstance]:
        """
        delete local volume
        return: api response
        """
        if self.create_local_volume is not None:
            api_response = None
            try:
                api_response = self.lv.delete(name=local_volume_name, namespace="openshift-local-storage")
            except ApiException as e:
                logger.exception(f"Exception while deleting Local Volume : {e}\n")
        else:
            logger.info("local volume is not create")
        return api_response


class LocalVolumeSet(LocalStorageOperator):
    """
    LocalVolumeSet Class extends LocalStorageOperator
    related to local volume set
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "local.storage.openshift.io/v1alpha1"
        self.kind = "LocalVolumeSet"
        self.lvs = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_local_volume_set(self, **kwargs) -> Optional[ResourceInstance]:
        """
        create local volume set
        :param local_volume_set_name:(required) name  of the local volume

        :return api response
        """
        if self.operator_version is not None and self.channel is not None and self.check_operator_install is True:
            csv = ClusterServiceVersion()
            csv_obj = csv.get_cluster_service_version(
                "local-storage-operator." + self.operator_version, "openshift-local-storage"
            )
            crd = csv_obj.metadata.annotations["alm-examples"]
            for i in range(0, len(eval(crd))):
                if "'kind': 'LocalVolumeSet', 'metadata'" in str(eval(crd)[i]):
                    target_item = i
            body = eval(crd)[target_item]
            if "name" in kwargs.keys():
                body["metadata"]["name"] = kwargs["name"]
            if "storageClassName" in kwargs.keys():
                body["spec"]["storageClassName"] = kwargs["storageClassName"]
            if "deviceTypes" in kwargs.keys():
                body["spec"]["deviceInclusionSpec"]["deviceTypes"] = kwargs["deviceTypes"]
            if "volumeMode" in kwargs.keys():
                body["spec"]["volumeMode"] = kwargs["volumeMode"]
            api_response = None
            try:
                api_response = self.lvs.create(namespace="openshift-local-storage", body=body)
            except ApiException as e:
                logger.exception(f"Exception while creating Local Volumeset : {e}\n")
        else:
            logger.info("local storage operator is not installed")
        return api_response

    def get_local_volume_set(self, namespace: str, local_volume_set_name: str) -> Optional[ResourceInstance]:
        """
        get local volume set
        param namespace: namespace of the local volume
        param local_volume_set_name: name of the local volume
        return: api response
        """
        api_response = None
        try:
            api_response = self.lvs.get(namespace=namespace, name=local_volume_set_name)
        except ApiException as e:
            logger.exception(f"Exception while creating Local Volume : {e}\n")
        return api_response

    def watch_local_volume_set(self, namespace: str, local_volume_set_name: str, timeout: int) -> bool:
        """
        watch local volume set
        param namespace: namespace of the local volume
        param local_volume_set_name: name of the local volume
        timeout: seconds for check
        return: is local volume ready (True | FALSE)
        """
        end = time() + timeout
        while time() < end:
            api_response = self.get_local_volume_set(namespace=namespace, local_volume_set_name=local_volume_set_name)
            if api_response.status is not None:
                break
            else:
                logger.info(f"local volume set {local_volume_set_name} status is present, waiting for ready state")
                continue
        if len(api_response.status.conditions) != 0:
            is_local_volume_set_ready = False
            field_selector = f"metadata.name={local_volume_set_name}"
            for event in self.lvs.watch(
                namespace="openshift-local-storage", field_selector=field_selector, timeout=timeout
            ):
                for condition in event["object"]["status"]["conditions"]:
                    if condition["status"] == "True":
                        logger.info(f"local volume set {local_volume_set_name} status is ready")
                        is_local_volume_set_ready = True
                        return is_local_volume_set_ready
                    else:
                        logger.info(f"local volume{local_volume_set_name} is waiting for ready state")
        else:
            logger.error(f"status for {local_volume_set_name} volume is not present")
        return is_local_volume_set_ready

    def delete_local_volume_set(self, local_volume_set_name: str) -> Optional[ResourceInstance]:
        """
        delete local volume set
        return: api response
        """
        if self.create_local_volume_set is not None:
            api_response = None
            try:
                api_response = self.lvs.delete(name=local_volume_set_name, namespace="openshift-local-storage")
            except ApiException as e:
                logger.exception(f"Exception while deleting Local Volume set : {e}\n")
        else:
            logger.info("local volume is not create")
        return api_response


class LocalVolumeDiscovery(LocalStorageOperator):
    """
    LocalVolumeDiscovery Class extends LocalStorageOperator
    related to ocal volume set
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "local.storage.openshift.io/v1alpha1"
        self.kind = "LocalVolumeDiscovery"
        self.lvd = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_local_volume_discovery(self, node_values: list) -> Optional[ResourceInstance]:
        """
        create local volume discovery
        :param local_volume_discovery_name:(required) name  of the local volume

        :return api response
        """
        if self.operator_version is not None and self.channel is not None and self.check_operator_install is True:
            csv = ClusterServiceVersion()
            csv_obj = csv.get_cluster_service_version(
                "local-storage-operator." + self.operator_version, "openshift-local-storage"
            )
            crd = csv_obj.metadata.annotations["alm-examples"]
            for i in range(0, len(eval(crd))):
                if "'kind': 'LocalVolumeDiscovery', 'metadata'" in str(eval(crd)[i]):
                    target_item = i
            body = eval(crd)[target_item]
            body["spec"]["nodeSelector"]["nodeSelectorTerms"][0]["matchExpressions"][0]["values"] = node_values
            api_response = None
            try:
                api_response = self.lvd.create(namespace="openshift-local-storage", body=body)
            except ApiException as e:
                logger.exception(f"Exception while creating Local Volumeset : {e}\n")
        else:
            logger.info("local storage operator is not installed")
        return api_response

    def get_local_volume_discovery(
        self, namespace: str, local_volume_discovery_name: str
    ) -> Optional[ResourceInstance]:
        """
        get local volume discovery
        param namespace: namespace of the local volume
        param local_volume_discovery_name: name of the local volume
        return: api response
        """
        api_response = None
        try:
            api_response = self.lvd.get(namespace=namespace, name=local_volume_discovery_name)
        except ApiException as e:
            logger.exception(f"Exception while creating Local Volume : {e}\n")
        return api_response

    def watch_local_volume_discovery(self, namespace: str, local_volume_discovery_name: str, timeout: int) -> bool:
        """
        watch local volume discovery
        param namespace: namespace of the local volume
        param local_volume_discovery_name: name of the local volume
        timeout: seconds for check
        return: is local volume ready (True | FALSE)
        """
        end = time() + timeout
        while time() < end:
            api_response = self.get_local_volume_discovery(
                namespace=namespace, local_volume_discovery_name=local_volume_discovery_name
            )
            if api_response.status is not None:
                break
            else:
                logger.info(
                    f"local volume discovery {local_volume_discovery_name} status is present, waiting for ready state"
                )
                continue
        if len(api_response.status.conditions) != 0:
            is_local_volume_discovery_ready = False
            field_selector = f"metadata.name={local_volume_discovery_name}"
            for event in self.lvd.watch(
                namespace="openshift-local-storage", field_selector=field_selector, timeout=timeout
            ):
                for condition in event["object"]["status"]["conditions"]:
                    if condition["status"] == "True":
                        logger.info(f"local volume discovery {local_volume_discovery_name} status is ready")
                        is_local_volume_discovery_ready = True
                        return is_local_volume_discovery_ready
                    else:
                        logger.info(f"local volume{local_volume_discovery_name} is waiting for ready state")
        else:
            logger.error(f"status for {local_volume_discovery_name} volume is not present")
        return is_local_volume_discovery_ready

    def delete_local_volume_discovery(self, local_volume_discovery_name: str) -> Optional[ResourceInstance]:
        """
        delete local volume discovery
        return: api response
        """
        if self.create_local_volume_discovery is not None:
            api_response = None
            try:
                api_response = self.lvd.delete(name=local_volume_discovery_name, namespace="openshift-local-storage")
            except ApiException as e:
                logger.exception(f"Exception while deleting Local Volume set : {e}\n")
        else:
            logger.info("local volume is not create")
        return api_response
