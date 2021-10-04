import logging

from openshift.dynamic.resource import ResourceInstance
import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpMachineHealthCheck, OcpMachines, OcpMachineSet, OcpNodes

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="session")
def get_test_objects(get_kubeconfig):
    """
    Prepare the test artifacts as an object and pass it as
    a fixture.
    """

    class TestObjects:
        def __init__(self):
            self.machine_health_check = OcpMachineHealthCheck(kube_config_file=get_kubeconfig)
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


@pytest.mark.skip_if_not_provider("BareMetal")
class TestOcpMachineHealthCheck:
    def test_get_all_machine_health_checks(self, get_test_objects):
        mhc_obj = get_test_objects.machine_health_check
        machine_health_check_list = mhc_obj.get_all_machine_health_checks()
        assert isinstance(machine_health_check_list, ResourceInstance)
        assert machine_health_check_list.kind == "MachineHealthCheckList"

    def test_get_machine_health_check(self, get_test_objects):
        mhc_obj = get_test_objects.machine_health_check
        machine_health_check_list = mhc_obj.get_all_machine_health_checks()
        machine_health_check_name = machine_health_check_list.items[0].metadata.name
        mhc_response_obj = mhc_obj.get_machine_health_check(machine_health_check_name)
        assert mhc_response_obj.kind == "MachineHealthCheck"
        assert mhc_response_obj.metadata.name == machine_health_check_name

    def test_machine_health_check_is_configured(self, get_test_objects):
        machine_health_check_name = "new-mhc"
        ms_obj = get_test_objects.machine_set
        machine_set_list = ms_obj.get_machine_sets()
        machine_set_name = machine_set_list.items[0].metadata.name
        is_mhc_configured = self._configure_machine_health_check(
            get_test_objects, machine_set_name, machine_health_check_name
        )
        assert is_mhc_configured is True

    def test_machine_health_check_is_not_configured(self, get_test_objects):
        machine_health_check_name = "new-mhc"
        # set random incorrect machine_set_name
        machine_set_name = "wrong_machine_set_name"
        is_mhc_configured = self._configure_machine_health_check(
            get_test_objects, machine_set_name, machine_health_check_name
        )
        assert is_mhc_configured is False

    def _configure_machine_health_check(
        self, get_test_objects, machine_set_name: str, machine_health_check_name: str
    ) -> bool:
        """
        Configure Machine Health Check for a machineset.
        :param machine_health_check_name: (str) name of the machine health check
        :param machine_set_name: (str) name of machine set name
        :return: (bool) True when successfully configured a Machine Heath Check object OR False otherwise
        """
        mhc_obj = get_test_objects.machine_health_check
        mhc_data = {
            "kind": "MachineHealthCheck",
            "spec": {
                "unhealthyConditions": [
                    {"status": "False", "type": "Ready", "timeout": "300s"},
                    {"status": "Unknown", "type": "Ready", "timeout": "300s"},
                ],
                "maxUnhealthy": "40%",
                "nodeStartupTimeout": "10m",
                "selector": {"matchLabels": {"machine.openshift.io/cluster-api-machineset": f"{machine_set_name}"}},
            },
            "apiVersion": "machine.openshift.io/v1beta1",
            "metadata": {"namespace": "openshift-machine-api", "name": f"{machine_health_check_name}"},
        }
        try:
            mhc_obj.create_machine_health_check(machine_set_name, machine_health_check_name, mhc_data)
            if not mhc_obj.is_machine_health_check_configured(machine_set_name, machine_health_check_name):
                logger.error("The Machine Health Check is not configured as none of the machines are healthy")
                return False
        except Exception:
            raise
        finally:
            mhc_obj.delete_machine_health_check(machine_health_check_name)
        return True
