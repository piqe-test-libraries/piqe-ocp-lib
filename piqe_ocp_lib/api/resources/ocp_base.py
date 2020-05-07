import yaml
from urllib3.exceptions import InsecureRequestWarning
from kubernetes import client, config
from openshift.dynamic import DynamicClient, Resource
from kubernetes.client.rest import ApiException
from subprocess import PIPE, Popen
import logging
import warnings
import requests
from piqe_ocp_lib import __loggername__

warnings.simplefilter('ignore', InsecureRequestWarning)

logger = logging.getLogger(__loggername__)


class OcpBase(object):

    def __init__(self, hostname='localhost', username='admin', password='redhat', kube_config_file=None):
        """
        The init method for the base class creates an instace of
        the openshift dynamic rest client based on either an
        authentication token or kube config file.
        :param hostname: (optional | str) The hostname/FQDN/IP of the master
                          node of the targeted OCP cluster. Defaults to
                          localhost if unspecified.
        :param username: (optional | str) login username. Defaults to admin
                          if unspecified.
        :param password: (optional | str) login password. Defaults to redhat
                          if unspecified.
                          TODO: Switch to encrypted passwords? If implemented,
                                it has to apply to all classes inheriting OcpBase.
        :param kube_config_file: A kubernetes config file. It overrides
                                 the hostname/username/password params
                                 if specified.
        :return: None
        """

        self.kube_config_file = kube_config_file
        self.hostname = hostname
        self.username = username
        self.password = password
        self.k8s_client = None

        if self.kube_config_file:
            self.k8s_client = config.new_client_from_config(str(self.kube_config_file))
        else:
            self._token = self.get_auth_token(host=self.hostname, username=self.username, password=self.password)
            configuration = client.Configuration()
            configuration.api_key['authorization'] = self._token
            configuration.api_key_prefix['authorization'] = 'Bearer'
            configuration.host = 'https://%s:8443' % hostname
            configuration.verify_ssl = False
            self.k8s_client = client.ApiClient(configuration)

        self.dyn_client = DynamicClient(self.k8s_client)

    def get_auth_token(self, host='localhost', username='admin', password='redhat'):
        """
        Method that returns a session token to be used for REST calls
        :param host: (optional | str) The hostname/fqdn/IP of the master node.
        :param username: (optional | str) The login username. Defaults to admin
        :param password: (optional | str) The login password. Defaults to redhat
        :return: Authentication token
        """
        try:
            p1 = Popen(["curl", "-sIk",
                        """https://%s:8443/oauth/authorize?response_type=token"""
                        """&client_id=openshift-challenging-client""" % host,
                        "--user", "%s:%s" % (username, password)], stdout=PIPE)
            p2 = Popen(["grep", "-oP", "access_token=\\K[^&]*"], stdin=p1.stdout, stdout=PIPE)
            p1.stdout.close()
        except ApiException as e:
            logger.exception("Exception was encountered while trying to obtain a session token: %s\n", e)
        token = p2.communicate()[0]
        return token.strip().decode('ascii')

    @property
    def version(self):
        return self._get_ocp_version

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
        # In the case of an OCP 3 cluster, the 'ClusterVersion' resource is not a thing, so our
        # try/except block above returns an empty list. Consequently, we need to resort to performing
        # a GET http request on the enpoint that maps to 'oc version'.
        # That is https://<api_server>:443/version/openshift?timeout=32s. This is obtained from the
        # output of 'oc version --loglevel=9'. The server name itself is retrieved directly from the
        # kubeconfig file.
        elif not api_response:
            # Open the kubeconfig file in read mode
            with open(self.kube_config_file, 'r') as f:
                # Collect the server lines/entries that have the
                # keyword 'server'
                server_entries = [line for line in f if 'server' in line]
                server_urls = []
                for server in server_entries:
                    # Separate and store just the urls
                    server_urls.append(server.strip().split(' ')[1])
                for url in server_urls:
                    # Initialize to None so we have something to return
                    # in case the procedure fails.
                    major = minor = None
                    try:
                        # Perform the GET http request
                        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                        response = requests.get(url + '/version/openshift?timeout=32s', verify=False)
                        if response.status_code == 200:
                            # The response is in string format, so we use eval to convert it to
                            # what it looks like to be, a dictionary
                            response_dict = eval(response.content)
                            # Retrieve the major and minor versions by key
                            major = response_dict['major']
                            # Minor is usually followed by a '+', as in version '3.11+'
                            # so we only keep numerical characters in the minor string.
                            minor = ''.join(char for char in response_dict['minor'] if char.isalnum())
                            """
                            Response Body: {
                              "major": "3",
                              "minor": "11+",
                              "gitVersion": "v3.11.157",
                              "gitCommit": "dfe38da0aa",
                              "gitTreeState": "",
                              "buildDate": "2019-12-02T08:30:15Z",
                              "goVersion": "",
                              "compiler": "",
                              "platform": ""
                            }
                            """
                            if response_dict["gitVersion"]:
                                z_stream = response_dict["gitVersion"].rsplit('.', 1)[1]
                            else:
                                z_stream = "0"
                            break
                        else:
                            continue
                    except requests.exceptions.RequestException as e:
                        logger.exception('Failed to perform request on {}: {}'.format(url, e))
                if not (major and minor):
                    logger.info('Failed to obtain version info from api server')
        return major, minor, z_stream

    def get_data_from_kubeconfig_v4(self):
        """
        Get required data from kubeconfig file provided by openshift
        - API Server URL
        - Access Token
        :return: (dict) Return dict in form of kubeconfig_data
        """
        kubeconfig_data = dict()
        api_server_url = None

        with open(self.kube_config_file) as f:
            kcfg = yaml.load(f, Loader=yaml.FullLoader)

            # Get API server URL
            logger.info("Find API Server URL from kubeconfig file")
            if 'clusters' in kcfg:
                clusters = kcfg['clusters']
                for cluster in clusters:
                    if "server" in cluster['cluster']:
                        api_server_url = cluster['cluster']['server']
                    if api_server_url:
                        break
            logger.info("API Server URL : %s", api_server_url)
            kubeconfig_data["api_server_url"] = api_server_url

        return kubeconfig_data
