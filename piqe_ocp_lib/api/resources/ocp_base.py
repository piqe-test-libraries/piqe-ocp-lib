from urllib3.exceptions import InsecureRequestWarning
from kubernetes import config
from openshift.dynamic import DynamicClient, Resource
from kubernetes.client.rest import ApiException
from threading import RLock
import logging
import warnings
from piqe_ocp_lib import __loggername__

warnings.simplefilter('ignore', InsecureRequestWarning)

logger = logging.getLogger(__loggername__)


class OcpBase(object):
    """
    This dict will hold kubeconfig as key and DynamicClient object as value
    """
    _dyn_clients = {}

    """
    This dict will hold kubeconfig as key and  kubernetes object, k8_client as value
    """
    k8s_clients = {}

    # For thread safe
    _lock = RLock()

    def __init__(self, kube_config_file=None):
        """
        The init method for the base class
        :return: None
        """
        # Lock the thread in case of multi-threading
        with OcpBase._lock:
            self.kube_config_file = kube_config_file

    @property
    def k8s_client(self):
        """
        Return k8s_client instance for specific openshift cluster based on kube_config_file attribute
        :return: Instance of K8s_client
        """
        if self.kube_config_file and self.kube_config_file not in OcpBase.k8s_clients:
            OcpBase.k8s_clients[self.kube_config_file] = config.new_client_from_config(str(self.kube_config_file))
        return OcpBase.k8s_clients.get(self.kube_config_file)

    @property
    def dyn_client(self):
        """
        Return dyn_client instance for specific openshift cluster based on kube_config_file attribute
        :return: Instance of DynamicClient
        """
        # Lock the thread in case of multi-threading
        with OcpBase._lock:
            if OcpBase._dyn_clients.get(self.kube_config_file) is None:
                OcpBase._dyn_clients[self.kube_config_file] = DynamicClient(self.k8s_client)
            return OcpBase._dyn_clients.get(self.kube_config_file)

    @property
    def version(self):
        """
        Return tuple of cluster version in the form (major, minor, z-stream)
        :return: (tuple) cluster version
        """
        return self._get_ocp_version()

    def _get_ocp_version(self):
        """
        Method that discovers the server version and returns it in the form of a tuple
        containing major and minor version.
        :return: A tuple containing the major version in string format at index 0,
                 the minor version in string format at index 1,
                 and z-stream version at index 2
        """
        try:
            # Using 'search' allows to check if a type of resource exists without throwing an
            # exception unlike using 'get'. If such resource is not found, an empty list is
            # returned. Otherwise, a list containing the sought after resource object is returned.
            api_response = self.dyn_client.resources.search(api_version='config.openshift.io/v1',
                                                            kind='ClusterVersion')
            assert isinstance(api_response, list)
        except ApiException as e:
            logger.exception("Exception was encountered while trying to obtain cluster version: {}".format(e))
        # Now that we have established that our api call returned a list, we check if we are dealing with an
        # OCP 3 or 4 cluster. This is simply achieved by checking wether the list is empty or not. When it is not
        # empty, we check that the resource type is 'ClusterVersion' just for good measure.
        if api_response and isinstance(api_response[0], Resource) and api_response[0].kind == 'ClusterVersion':
            api_response = api_response[0]
            # We get the actual ClusterVersion object
            cluster_version_obj = api_response.get()
            # Version is under obj.status.history. History is a list of dict and we want
            # to get the version with state="Completed" entry incase if there are fail entries in histories
            version_histories = cluster_version_obj.items[0].status.history
            # Sort the version history list by startedTime in descending order so that last update history
            # will be the first to check
            sorted_version_histories = sorted(version_histories, key=lambda k: k['startedTime'], reverse=True)
            # It's in string form, so we turn it into a list so we can use indexing
            # to easily retrieve major and minor versions
            for history in sorted_version_histories:
                if history.state == "Completed":
                    version_list = history.version.split('.', 2)
                    major = str(version_list[0])
                    minor = str(version_list[1])
                    z_stream = str(version_list[2].split("-")[0])
                    break
        return major, minor, z_stream
