from enum import Enum
import logging
from typing import Dict, Optional

from kubernetes.client import Configuration
from kubernetes.client.rest import ApiException
import requests

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpBase

logger = logging.getLogger(__loggername__)


class VirtualMachineActions(str, Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"


class VirtualMachineSubResourcesClient:
    """
    Replace this class as soon as the following issues are fixed in kubevirt:
        - https://github.com/kubevirt/client-python/issues/29 (Wrong URL replacement)
        - https://github.com/kubevirt/client-python/issues/28 (No auth header)
    """

    __slots__ = ("name", "namespace", "api_version", "config")

    def __init__(self, name: str, namespace: str, api_version: str, config: Configuration):
        self.name = name
        self.namespace = namespace
        self.api_version = api_version
        self.config = config

    @property
    def base_url(self):
        return (
            f"{self.config.host}/apis/subresources.kubevirt.io/"
            f"{self.api_version}/namespaces/{self.namespace}/virtualmachines/{self.name}"
        )

    def run_action(self, action: VirtualMachineActions):
        action_url = f"{self.base_url}/{action}"
        return requests.put(action_url, verify=self.config.verify_ssl, headers=self.config.api_key)


class OcpVirtualMachines(OcpBase):
    """
    Extends OcpBase and encapsulates all methods related to managing Openshift VirtualMachines.
    Higher level abstraction to REST API.
    :param kube_config_file: A kubernetes config file.
    :param subresources_config: A Configuration class for VirtualMachineSubResourcesClient
    """

    __slots__ = ("api_version", "kind", "client", "subresources_config")

    def __init__(self, kube_config_file: Optional[str] = None, subresources_config: Optional[Configuration] = None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "kubevirt.io/v1alpha3"
        self.kind = "VirtualMachine"

        self.client = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
        self.subresources_config = subresources_config or self.k8s_client.configuration

    def _get_subresources_client(self, name: str, namespace: str):
        api_version = self.api_version.split("/")[1]
        return VirtualMachineSubResourcesClient(name, namespace, api_version, self.subresources_config)

    def create(self, namespace: str, spec: Dict):
        try:
            return self.client.create(namespace=namespace, body=spec)
        except ApiException as exc:
            logger.exception(f"Exception while deploying VirtualMachine with spec: {spec}")
            raise exc

    def delete(self, name: str, namespace: str):
        return self.client.delete(namespace=namespace, name=name)

    def get_status(self, name: str, namespace: str):
        response = self.client.status.get(name=name, namespace=namespace)
        return response.status

    def run_action(self, name: str, namespace: str, action: VirtualMachineActions):
        cli = self._get_subresources_client(name, namespace)
        response = cli.run_action(action)
        return response.ok


class VirtualMachine:
    """
    Provides methods to deal with VirtualMachines. Current API mimics human
    interactions with virtual machines
    """

    def __init__(self, name: str, namespace: str, resource: Optional[OcpBase] = None, spec: Optional[Dict] = None):
        self.name: str = name
        self.namespace: str = namespace
        self.resource: OcpVirtualMachines = resource or OcpVirtualMachines()

        self.spec: Dict = spec or {}

    @property
    def spec(self) -> Dict:
        return self._spec

    @spec.setter
    def spec(self, value: Dict) -> None:
        spec = {
            "kind": self.resource.kind,
            "apiVersion": self.resource.api_version,
            "metadata": {"name": self.name},
            "spec": value,
        }

        self._spec = spec

    @property
    def status(self):
        return self.resource.get_status(self.name, self.namespace)

    def __enter__(self):
        return self.deploy()

    def __exit__(self, *args):
        self.delete()

    def __repr__(self) -> str:
        return f"VirtualMachine(name={self.name}, namespace={self.namespace})"

    def deploy(self):
        return self.resource.create(self.namespace, self.spec)

    def delete(self):
        return self.resource.delete(self.name, self.namespace)

    def start(self) -> bool:
        return self.resource.run_action(self.name, self.namespace, VirtualMachineActions.START)

    def stop(self) -> bool:
        return self.resource.run_action(self.name, self.namespace, VirtualMachineActions.STOP)

    def restart(self) -> bool:
        return self.resource.run_action(self.name, self.namespace, VirtualMachineActions.RESTART)
