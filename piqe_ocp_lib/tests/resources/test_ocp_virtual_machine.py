from unittest import mock

from kubernetes.client import Configuration
import pytest

from piqe_ocp_lib.api.resources.ocp_virtual_machine import (
    OcpVirtualMachines,
    VirtualMachine,
    VirtualMachineActions,
    VirtualMachineSubResourcesClient,
)


@pytest.fixture(scope="module")
def vm_name() -> str:
    return "quick"


@pytest.fixture(scope="module")
def vm_namespace() -> str:
    return "fox"


@pytest.fixture(scope="module")
def vm_api_version() -> str:
    return "kubevirt.io/v1alpha3"


@pytest.fixture(scope="module")
def k8s_default_config() -> Configuration:
    return Configuration()


@pytest.fixture(scope="module")
def ocp_vm_resource(get_kubeconfig) -> OcpVirtualMachines:
    return OcpVirtualMachines(get_kubeconfig)


@pytest.fixture(scope="module")
def default_vm(vm_name, vm_namespace) -> OcpVirtualMachines:
    return VirtualMachine(vm_name, vm_namespace)


@pytest.mark.unit
def test_vm_subresources_client_base_url(vm_name, vm_namespace, vm_api_version, k8s_default_config):
    expected_result = (
        f"{k8s_default_config.host}/apis/subresources.kubevirt.io/"
        f"{vm_api_version}/namespaces/{vm_namespace}/virtualmachines/{vm_name}"
    )

    client = VirtualMachineSubResourcesClient(vm_name, vm_namespace, vm_api_version, k8s_default_config)

    result = client.base_url

    assert result == expected_result


@pytest.mark.unit
@mock.patch("requests.put")
@mock.patch.object(
    VirtualMachineSubResourcesClient, "base_url", new_callable=mock.PropertyMock(return_value="http://foo.bar")
)
@pytest.mark.parametrize(
    "action,expected_url", [(action, f"http://foo.bar/{action}") for action in VirtualMachineActions]
)
def test_vm_subresources_client_run_action(
    _, mock_requests, vm_name, vm_namespace, vm_api_version, k8s_default_config, action, expected_url
):
    cli = VirtualMachineSubResourcesClient(vm_name, vm_namespace, vm_api_version, k8s_default_config)

    cli.run_action(action)

    mock_requests.assert_called_once_with(
        expected_url, verify=k8s_default_config.verify_ssl, headers=k8s_default_config.api_key
    )


@pytest.mark.unit
def test_ocp_virtual_machine_custom_subresource_config(get_kubeconfig, vm_name, vm_namespace):
    config = Configuration()
    config.debug = True

    resource = OcpVirtualMachines(get_kubeconfig, subresources_config=config)
    client = resource._get_subresources_client(vm_name, vm_namespace)

    assert client.config == config


@pytest.mark.unit
def test_ocp_virtual_machine_create(ocp_vm_resource, vm_namespace):
    with mock.patch.object(ocp_vm_resource, "client") as mock_client:
        ocp_vm_resource.create(vm_namespace, {})
        mock_client.create.assert_called_once_with(namespace=vm_namespace, body={})


@pytest.mark.unit
def test_ocp_virtual_machine_delete(ocp_vm_resource, vm_name, vm_namespace):
    with mock.patch.object(ocp_vm_resource, "client") as mock_client:
        ocp_vm_resource.delete(vm_name, vm_namespace)
        mock_client.delete.assert_called_once_with(name=vm_name, namespace=vm_namespace)


@pytest.mark.unit
def test_ocp_virtual_machine_get_status(ocp_vm_resource, vm_name, vm_namespace):
    with mock.patch.object(ocp_vm_resource, "client") as mock_client:
        ocp_vm_resource.get_status(vm_name, vm_namespace)
        mock_client.status.get.assert_called_once_with(name=vm_name, namespace=vm_namespace)


@pytest.mark.unit
def test_ocp_virtual_machine_run_action(ocp_vm_resource, vm_name, vm_namespace):
    action = VirtualMachineActions.START
    with mock.patch.object(ocp_vm_resource, "_get_subresources_client", return_value=mock.Mock()) as mock_subresource:

        ocp_vm_resource.run_action(vm_name, vm_namespace, action=action)

        mock_subresource.assert_called_once_with(vm_name, vm_namespace)
        mock_subresource.return_value.run_action.assert_called_once_with(action)


@pytest.mark.unit
def test_virtual_machine_spec_setter(default_vm):
    assert default_vm.spec == {
        "kind": default_vm.resource.kind,
        "apiVersion": default_vm.resource.api_version,
        "metadata": {"name": default_vm.name},
        "spec": {},
    }


@pytest.mark.unit
def test_virtual_machine_status_property(default_vm):
    with mock.patch.object(default_vm, "resource") as mocked_resource:
        mocked_resource.get_status.return_value = mock.sentinel.status

        result = default_vm.status

        mocked_resource.get_status.assert_called_once_with(default_vm.name, default_vm.namespace)
        assert result == mock.sentinel.status


@pytest.mark.unit
def test_virtual_machine_repr(default_vm):
    assert repr(default_vm) == f"VirtualMachine(name={default_vm.name}, namespace={default_vm.namespace})"


@pytest.mark.unit
def test_virtual_machine_context(default_vm):

    with mock.patch.object(default_vm, "delete") as mock_delete:
        with mock.patch.object(default_vm, "deploy") as mock_deploy:
            with default_vm:
                pass

            mock_deploy.assert_called_once()
        mock_delete.assert_called_once()
