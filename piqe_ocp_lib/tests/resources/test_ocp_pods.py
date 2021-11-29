import logging

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpNodes, OcpPods

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="class")
def setup_params(get_kubeconfig):
    params_dict = {}
    params_dict["pods_api_obj"] = OcpPods(kube_config_file=get_kubeconfig)
    params_dict["nodes_api_obj"] = OcpNodes(kube_config_file=get_kubeconfig)
    return params_dict


class TestOcpPods:
    def test_list_of_pods_in_a_node(self, setup_params):
        """
        Verify that list of pods are returned for a node_name
        1. Call list_of_pods_in_a_node method via a ocp_pods instance
        2. Verify len of list is not zero.
        :param setup_params:
        :return:
        """
        pods_api_obj = setup_params["pods_api_obj"]
        nodes_api_obj = setup_params["nodes_api_obj"]
        node_name_list = []
        pod_exists = False
        api_response = nodes_api_obj.get_worker_nodes()
        for item in api_response.items:
            node_name_list.append(item["metadata"]["name"])
        for node in node_name_list:
            pods_list = pods_api_obj.list_of_pods_in_a_node(node)
            if len(pods_list) > 0:
                pod_exists = True
        assert pod_exists is True
