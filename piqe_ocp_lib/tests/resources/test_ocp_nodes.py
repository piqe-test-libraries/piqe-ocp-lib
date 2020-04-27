from piqe_ocp_lib.api.resources import OcpNodes
import pytest
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope='class')
def setup_params(get_kubeconfig):
    params_dict = {}
    params_dict['node_api_obj'] = OcpNodes(kube_config_file=get_kubeconfig)
    return params_dict


class TestOcpNodes(object):

    def test_get_all_nodes(self, setup_params):
        """
        Verify that a list of all nodes is returned
        1. Call get_all_nodes method via a ocp_nodes instance
        2. Verify that the response object is of kind NodeList
        :param setup_params:
        :return:
        """
        node_api_obj = setup_params['node_api_obj']
        # Get all nodes
        api_response = node_api_obj.get_all_nodes()
        node_count = len(api_response.items)
        logger.info("{} nodes returned in the list".format(node_count))
        assert api_response.kind == 'NodeList'

        # Get nodes matching a single label
        api_response = node_api_obj.get_all_nodes(label_selector='beta.kubernetes.io/os')
        list_items_single_label = len(api_response.items)
        # All nodes are expected to have this label, validate that the list counts match.
        assert list_items_single_label == node_count
        logger.info("{} nodes matched the provided label".format(list_items_single_label))
        assert api_response.kind == 'NodeList'
        # Get nodes matching 2 labels
        api_response = node_api_obj.get_all_nodes(label_selector='beta.kubernetes.io/os=linux,'
                                                                 'node.openshift.io/os_id=rhcos')
        list_items_two_labels = len(api_response.items)
        # All nodes are expected to have these labels, validate that the list counts match.
        assert list_items_two_labels == node_count
        logger.info("{} nodes matched the provided label".format(list_items_two_labels))
        assert api_response.kind == 'NodeList'

    def test_get_all_node_names(self, setup_params):
        """
        Verify that node name lists are returned.
        1. Call get_all_nodes method via a ocp_nodes instance
        2. Verify that the response object type is a List
        :param setup_params:
        :return:
        """
        node_api_obj = setup_params['node_api_obj']
        api_response = node_api_obj.get_all_node_names()
        assert type(api_response) is list
        logger.info("Node name list: {}".format(api_response))
        assert len(api_response) > 0

    def test_get_a_node(self, setup_params):
        """
        Verify that nodes are returned by name
        1. Call get_all_nodes method via a ocp_nodes instance
        2. Verify that the response object is of kind NodeList
        :param setup_params:
        :return:
        """
        node_api_obj = setup_params['node_api_obj']
        api_response_node_name_list = node_api_obj.get_all_node_names()
        number_of_nodes = len(api_response_node_name_list)
        assert number_of_nodes > 0
        logger.info("{} Nodes returned".format(number_of_nodes))
        for node_name in api_response_node_name_list:
            # Use each node name from the list to get_a_node by mane.
            api_response = node_api_obj.get_a_node(node_name=node_name)
            assert api_response.kind == 'Node'
            # Evaluate Use addresses list to find the type Hostname
            assert api_response.metadata.name == node_name
        # Attempt to fetch a node that does not exist.
        # The method under test is expected to log an exception and return None
        api_response_not_found = node_api_obj.get_a_node(node_name='non_existent_node')
        assert api_response_not_found is None

    def test_get_status_of_a_node(self, setup_params):
        """
        Verify that node status is returned.
        1. Get a list of all nodes and validate that the list is not empty.
        2. Iterate through the list of node names and get the status of each node.
        3. Validate that each node returns status: True
        :param setup_params:
        :return:
        """
        node_api_obj = setup_params['node_api_obj']
        api_response_node_name_list = node_api_obj.get_all_node_names()
        assert len(api_response_node_name_list) > 0
        for node_name in api_response_node_name_list:
            # Use each node name from the list to get the node status by name
            api_response_node_status = node_api_obj.get_node_status(node_name=node_name)
            assert api_response_node_status == 'True'

    def test_get_node_roles(self, setup_params):
        """
        Verify that the node roles are returned and validate that either Master or Worker
        (or both) are assigned to the node.
        1. Get a list of the node names
        2. Iterate through the list and fetch the roles for each node.
        3. Validate that the returned list has at least one item.
        4. Validate that the content represents either Master or Worker roles.
        :param setup_params:
        :return:
        """
        node_api_obj = setup_params['node_api_obj']
        api_response_node_name_list = node_api_obj.get_all_node_names()
        for node_name in api_response_node_name_list:
            # Use each node name from the list to get the node status by name
            api_response_node_roles = node_api_obj.get_node_roles(node_name=node_name)
            logger.info("Retrieved {} roles for node {}".format(api_response_node_roles, node_name))
            number_of_roles = len(api_response_node_roles)
            assert number_of_roles >= 1
            for role in api_response_node_roles:
                logger.info("Node name: {} Role: {}".format(node_name, role))
                assert role == 'Master' or role == 'Worker'

    def test_label_a_node(self, setup_params):
        """
        Test creating a label on a node.
        1. Get a list of all node names
        2. Iterate through the list to get the Nodes based on their name.
        3. Validate that the returned Node matches the name.
        4. Label the node using a new key:value
        5. Call get all nodes, filtering the nodes by label to fetch the same node. This validates that the newly
           created label can be used to filter out the node.
        6. Validate the returned node by name using metadata.name and status.addresses.address.type and .address.
        """
        node_api_obj = setup_params['node_api_obj']
        api_response_node_name_list = node_api_obj.get_all_node_names()
        for node_name in api_response_node_name_list:
            api_response = node_api_obj.get_a_node(node_name=node_name)
            assert api_response.kind == 'Node'
            assert api_response.metadata.name == node_name
            # Label the node
            node_label = {'test.label.node': 'true'}
            logger.info("Label the Node with {}".format(node_label))
            label_api_response = node_api_obj.label_a_node(node_name=node_name, labels=node_label)
            assert label_api_response.kind == 'Node'
            assert label_api_response.metadata.name == node_name
            # Now fetch the node using the created filter.
            labelled_node_api_response = node_api_obj.get_all_nodes(label_selector='test.label.node=true,'
                                                                    'kubernetes.io/hostname=' + node_name)
            logger.info("Retrieved the node by labels {}".format(labelled_node_api_response.items[0].metadata.name))
            assert len(labelled_node_api_response.items) == 1
            assert labelled_node_api_response.items[0].metadata.name == node_name
            logger.info("Retrieved the node by labels {}".format(labelled_node_api_response.items[0].
                                                                 metadata.name))
            # Evaluate Use addresses list to find the type Hostname
            for address in labelled_node_api_response.items[0].status.addresses:
                if address.type == 'Hostname':
                    logger.info("Address Type: {}  Address: {}".format(address.type, address.address))
                    # Validate that the node name is the same as the hostname for the node.
                    assert address.address == node_name

    @pytest.mark.skip(reason="MPQEENABLE-396 expected_retcode assertion fails")
    def test_execute_command_on_a_node(self, setup_params):
        """
        On each node perform the following:
        1. Execute a valid command on the node and validate the return code indicates success,
           that stdout contains the expected output and that stderr is empty.
        2. Execute an invalid command on the node and validate the return code indicates failure,
           that stdout is empty and that stderr contains an error message.
        :param setup_params:
        :return:
        """
        node_api_obj = setup_params['node_api_obj']
        api_response_node_name_list = node_api_obj.get_all_node_names()
        # Validate stdout
        for node_name in api_response_node_name_list:
            api_response = node_api_obj.get_a_node(node_name=node_name)
            assert api_response.kind == 'Node'
            assert api_response.metadata.name == node_name
            logger.info("Execute command on Node {}".format(node_name))
            command_api_response = node_api_obj.execute_command_on_a_node(node_name=node_name,
                                                                          command_to_execute='whoami')
            expected_retcode = 0
            expected_stdout = b'root\n'
            expected_stderr = b''
            assert command_api_response[0] == expected_retcode
            assert type(command_api_response[1]) is bytes
            assert command_api_response[1] == expected_stdout
            assert command_api_response[2] == expected_stderr
            decoded_str = command_api_response[1].decode("utf-8")
            logger.info("Decoded stdout string {}".format(decoded_str))

        # Validate stderr
        for node_name in api_response_node_name_list:
            api_response = node_api_obj.get_a_node(node_name=node_name)
            assert api_response.kind == 'Node'
            assert api_response.metadata.name == node_name
            logger.info("Execute command on Node {}".format(node_name))
            command_api_response = node_api_obj.execute_command_on_a_node(node_name=node_name,
                                                                          command_to_execute='bogus')
            expected_retcode = 1
            expected_stdout = b''
            assert command_api_response[0] == expected_retcode
            assert command_api_response[1] == expected_stdout
            assert type(command_api_response[2]) is bytes
            decoded_str = command_api_response[2].decode("utf-8")
            logger.info("Decoded stderr string {}".format(decoded_str))
            assert decoded_str.find('executable file not found in $PATH') >= 1
