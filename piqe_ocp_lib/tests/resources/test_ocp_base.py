import logging
from threading import Thread
from queue import Queue

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import Version
from piqe_ocp_lib.api.resources import OcpBase

logger = logging.getLogger(__loggername__)


class TestOcpBase(object):
    def test_init(self, get_kubeconfig):
        base_api_obj = OcpBase(kube_config_file=get_kubeconfig)
        assert base_api_obj.kube_config_file is not None

    def test_version(self, get_kubeconfig):
        base_api_obj = OcpBase(kube_config_file=get_kubeconfig)

        version = base_api_obj.ocp_version

        assert isinstance(version, Version)

    def test_dynamic_client_singleton_for_ocp4x(self, get_kubeconfig):
        logger.info("Create two instances (ocp_base1 and ocp_base2) using kubeconfig of openshift 4x cluster")
        ocp_base1 = OcpBase(kube_config_file=get_kubeconfig)
        logger.info("Address of ocp_base1 object is %s", ocp_base1.dyn_client)
        ocp_base2 = OcpBase(kube_config_file=get_kubeconfig)
        logger.info("Address of ocp_base2 object is %s", ocp_base2.dyn_client)

        logger.info("Compare dynamic clients instances for kubeconfig")
        assert ocp_base1.dyn_client is ocp_base2.dyn_client

    def test_dynamic_client_singleton_multi_thread(self, get_kubeconfig):
        def test_singleton(kube_config_file, my_queue):
            ocp_base = OcpBase(kube_config_file=kube_config_file)
            my_queue.put(ocp_base.dyn_client)

        logger.info("Create three instances of dynamic client")
        threads = list()
        thread_queue = Queue()
        kube_config_files = [get_kubeconfig, get_kubeconfig]
        for kube_config_file in kube_config_files:
            thread = Thread(
                target=test_singleton,
                args=(
                    kube_config_file,
                    thread_queue,
                ),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        dynamic_client1, dynamic_client2 = thread_queue.queue
        logger.info("Dynamic_Client1 : %s", dynamic_client1)
        logger.info("Dynamic_Client2 : %s", dynamic_client2)
        assert dynamic_client1 is dynamic_client2

    # def test_dynamic_client_singleton_for_ocp3x(self, get_kubeconfig_3x):
    #     logger.info("Create two instances (ocp_base3 and ocp_base4) using kubeconfig of openshift 3x cluster")
    #     ocp_base3 = OcpBase(kube_config_file=get_kubeconfig_3x)
    #     logger.info("Address of ocp_base3 object is %s", ocp_base3.dyn_client)
    #     ocp_base4 = OcpBase(kube_config_file=get_kubeconfig_3x)
    #     logger.info("Address of ocp_base4 object is %s", ocp_base4.dyn_client)
    #
    #     logger.info("Compare dynamic clients instances for kubeconfig_3x")
    #     assert ocp_base3.dyn_client is ocp_base4.dyn_client

    # def test_dynamic_client_singleton_for_ocp3x_ocp4x(self, get_kubeconfig, get_kubeconfig_3x):
    #     logger.info("Create two instances (ocp_base3 and ocp_base4) using kubeconfig of openshift 3x and 4x cluster")
    #     ocp_base1 = OcpBase(kube_config_file=get_kubeconfig)
    #     logger.info("Address of ocp_base1 object is %s", ocp_base1.dyn_client)
    #     ocp_base3 = OcpBase(kube_config_file=get_kubeconfig_3x)
    #     logger.info("Address of ocp_base3 object is %s", ocp_base3.dyn_client)
    #
    #     logger.info("Compare dynamic clients instances for kubeconfig and kubeconfig_3x")
    #     assert ocp_base1.dyn_client is not ocp_base3.dyn_client

    # def test_dynamic_client_singleton_multi_thread(self, get_kubeconfig, get_kubeconfig_3x):
    #     def test_singleton(kube_config_file, my_queue):
    #         ocp_base = OcpBase(kube_config_file=kube_config_file)
    #         my_queue.put(ocp_base.dyn_client)
    #
    #     logger.info("Create three instances of dynamic client")
    #     threads = list()
    #     thread_queue = Queue()
    #     kube_config_files = [get_kubeconfig, get_kubeconfig, get_kubeconfig_3x]
    #     for kube_config_file in kube_config_files:
    #         thread = Thread(target=test_singleton, args=(kube_config_file, thread_queue,))
    #         threads.append(thread)
    #         thread.start()
    #
    #     for thread in threads:
    #         thread.join()
    #
    #     dynamic_client1, dynamic_client2, dynamic_client3 = thread_queue.queue
    #     logger.info("Dynamic_Client1 : %s", dynamic_client1)
    #     logger.info("Dynamic_Client2 : %s", dynamic_client2)
    #     logger.info("Dynamic_Client3 : %s", dynamic_client3)
    #     assert dynamic_client1 is dynamic_client2
    #     assert dynamic_client1 is not dynamic_client3

    # def test_k8s_client(self, get_kubeconfig, get_kubeconfig_3x):
    #     logger.info("Create two instances (ocp_base1 and ocp_base2) using kubeconfig of openshift 3x and 4x cluster")
    #     ocp_base1 = OcpBase(kube_config_file=get_kubeconfig)
    #     logger.info("Address of ocp_base1 object is %s", ocp_base1.k8s_client)
    #     ocp_base2 = OcpBase(kube_config_file=get_kubeconfig_3x)
    #     logger.info("Address of ocp_base3 object is %s", ocp_base2.k8s_client)
    #
    #     logger.info("Compare dynamic clients instances for kubeconfig and kubeconfig_3x")
    #     assert ocp_base1.k8s_client is not ocp_base2.k8s_client
