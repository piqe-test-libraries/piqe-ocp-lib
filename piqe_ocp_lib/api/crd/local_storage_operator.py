import logging
from time import sleep
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
        self.check_operator_install = self.oi_obj.check_operator_installed("local-storage-operator")
        if self.check_operator_install is None:
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

        :return api reponse
        """
        sleep(60)
        if not [x for x in (self.check_operator_install, self.operator_version, self.channel) if x is None]:
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

    def get_local_volume(self) -> Optional[ResourceInstance]:
        """
        get local volume
        return: api response
        """
        if self.create_local_volume is not None:
            api_response = None
            try:
                api_response = self.lv.get()
            except ApiException as e:
                logger.exception(f"Exception while creating Local Volume : {e}\n")
        else:
            logger.info("local volume is not created")
        return api_response

    def watch_local_volume(self, local_volume_name: str) -> bool:
        """
        watch local volume
        :param local_volume_name: name of the local volume
        return: is local volume ready (True | FALSE)
        """
        is_local_volume_ready = False
        field_selector = f"metadata.name={local_volume_name}"
        for event in self.lv.watch(namespace="openshift-local-storage", field_selector=field_selector, timeout=120):
            for condition in event["object"]["status"]["conditions"]:
                if condition["message"] == "Ready":
                    logger.info("local volume %s created successfully", local_volume_name)
                    is_local_volume_ready = True
                    return is_local_volume_ready
        logger.error("local volume %s failed", local_volume_name)
        return is_local_volume_ready

    def delete_local_volume(self, local_volume_name) -> Optional[ResourceInstance]:
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
