import logging

from openshift.dynamic.resource import ResourceInstance
import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpMachines, OcpMachineSet, OcpNodes

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="session")
def get_test_objects(get_kubeconfig):
    """
    Prepare the test artifacts as an object and pass it as
    a fixture.
    """

    class TestObjects:
        def __init__(self):
            self.machine_set = OcpMachineSet(kube_config_file=get_kubeconfig)
            self.machine = OcpMachines(kube_config_file=get_kubeconfig)
            self.node = OcpNodes(kube_config_file=get_kubeconfig)

    test_objs = TestObjects()
    return test_objs


@pytest.fixture(autouse=True)
def required_provider(request, get_test_objects):
    """
    We create a custom marker called 'skip_if_not_provider' and pass it
    the specific infrastructure provider this test expects.
    We look for that marker in request.node using get_closest_marker,
    if it's there, we check desired provider against detected provider
    that is obtained via the base class. If we don't have a match,
    we explicitly skip using pytest.skip()
    ---
    Decorate class or method with
    @pytest.mark.skip_if_not_provider('Azure')
    ---
    """
    skip_marker = request.node.get_closest_marker("skip_if_not_provider")
    if not skip_marker:
        return
    else:
        desired_provider = skip_marker.args[0]
    if desired_provider != get_test_objects.machine_set.provider:
        logger.warning(
            "The current test module requires provider: {}, "
            "but provider {} was detected".format(desired_provider, get_test_objects.machine_set.provider)
        )
        pytest.skip()


@pytest.mark.skip_if_not_provider("Azure")
class TestOcpMachineSet:
    def test_get_machine_sets(self, get_test_objects):
        ms_obj = get_test_objects.machine_set
        machine_set_list = ms_obj.get_machine_sets()
        assert isinstance(machine_set_list, ResourceInstance)
        assert machine_set_list.kind == "MachineSetList"

    def test_get_machine_set(self, get_test_objects):
        ms_obj = get_test_objects.machine_set
        machine_set_list = ms_obj.get_machine_sets()
        machine_set_name = machine_set_list.items[0].metadata.name
        machine_set_response_obj = ms_obj.get_machine_set(machine_set_name)
        assert machine_set_response_obj.kind == "MachineSet"
        assert machine_set_response_obj.metadata.name == machine_set_name

    def test_get_machine_set_role(self, get_test_objects):
        ms_obj = get_test_objects.machine_set
        machine_set_list = ms_obj.get_machine_sets()
        machine_set_name = machine_set_list.items[0].metadata.name
        machine_set_role = ms_obj.get_machine_set_role(machine_set_name)
        assert isinstance(machine_set_role, str)

    def test_is_machine_set_ready(self, get_test_objects):
        ms_obj = get_test_objects.machine_set
        machine_set_list = ms_obj.get_machine_sets()
        machine_set_name = machine_set_list.items[0].metadata.name
        state = ms_obj.is_machine_set_ready(machine_set_name)
        assert isinstance(state, bool)

    def test_scale_machine_set(self, get_test_objects):
        ms_obj = get_test_objects.machine_set
        machine_set_list = ms_obj.get_machine_sets()
        machine_set_name = machine_set_list.items[0].metadata.name
        machine_set_response_obj = ms_obj.get_machine_set(machine_set_name)
        initial_replica_count = machine_set_response_obj.spec.replicas
        scale_up_replicas = initial_replica_count + 1
        scale_up_result = ms_obj.scale_machine_set(machine_set_name, scale_up_replicas)
        assert scale_up_result is True
        scale_down_result = ms_obj.scale_machine_set(machine_set_name, initial_replica_count)
        assert scale_down_result is True


@pytest.mark.skip_if_not_provider("Azure")
class TestOcpMachines:
    def test_get_machines(self, get_test_objects):
        m_obj = get_test_objects.machine
        machine_list = m_obj.get_machines()
        assert isinstance(machine_list, ResourceInstance)
        assert machine_list.kind == "MachineList"

    def test_get_machine(self, get_test_objects):
        m_obj = get_test_objects.machine
        machine_list = m_obj.get_machines()
        machine_name = machine_list.items[0].metadata.name
        machine_response_obj = m_obj.get_machine(machine_name)
        assert machine_response_obj.kind == "Machine"
        assert machine_response_obj.metadata.name == machine_name

    def test_get_machines_by_role(self, get_test_objects):
        m_obj = get_test_objects.machine
        ms_obj = get_test_objects.machine_set
        ROLE_LABEL = "machine.openshift.io/cluster-api-machine-role"
        machine_set_list = ms_obj.get_machine_sets()
        machine_set_name = machine_set_list.items[0].metadata.name
        machine_set_response_obj = ms_obj.get_machine_set(machine_set_name)
        machine_set_role = machine_set_response_obj.metadata.labels[ROLE_LABEL]
        machines_list = m_obj.get_machines_by_role(machine_set_role).items
        sample_machine = machines_list[0]
        assert sample_machine.metadata.labels[ROLE_LABEL] == machine_set_role

    def test_get_parent_machine_set(self, get_test_objects):
        m_obj = get_test_objects.machine
        ms_obj = get_test_objects.machine_set
        worker_machine = m_obj.get_machines_by_role("worker").items[0]
        machine_set = m_obj.get_parent_machine_set(worker_machine.metadata.name)
        machine_set_response_obj = ms_obj.get_machine_set(machine_set)
        assert machine_set_response_obj.kind == "MachineSet"
        assert machine_set_response_obj.metadata.name == machine_set

    def test_get_machines_in_machineset(self, get_test_objects):
        m_obj = get_test_objects.machine
        ms_obj = get_test_objects.machine_set
        machine_set_list = ms_obj.get_machine_sets()
        machine_set_name = machine_set_list.items[0].metadata.name
        machines_list = m_obj.get_machines_in_machineset(machine_set_name).items
        for machine in machines_list:
            assert machine.kind == "Machine"

    def test_get_machine_node_ref(self, get_test_objects):
        m_obj = get_test_objects.machine
        node_obj = get_test_objects.node
        worker_machine = m_obj.get_machines_by_role("worker").items[0]
        node_name = m_obj.get_machine_node_ref(worker_machine.metadata.name)
        node_obj = node_obj.get_a_node(node_name)
        assert node_obj.kind == "Node"
        assert node_obj.metadata.name == node_name
