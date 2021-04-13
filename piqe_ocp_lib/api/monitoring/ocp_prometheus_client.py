import requests
import logging
import warnings
from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from piqe_ocp_lib.api.resources.ocp_secrets import OcpSecret
from piqe_ocp_lib.api.resources.ocp_routes import OcpRoutes
from requests.exceptions import RequestException, ConnectionError, HTTPError
from urllib3.exceptions import InsecureRequestWarning
from piqe_ocp_lib import __loggername__

warnings.simplefilter("ignore", InsecureRequestWarning)

logger = logging.getLogger(__loggername__)

"""
OcpPrometheusClient is created by using openshift prometheus route, prometheus secret token and python request module.
Using this client, User can query openshift prometheus DB to retrieve cluster labels and it's stats, cluster jobs and
current status.
i.e.

    https://prometheus.io/docs/prometheus/latest/querying/api/

    curl -kv -H "Authorization: bearer $( oc whoami --show-token )"
    "https://<prometheus_route>:443/<prometheus_api_path>"

    Label Query :
    curl -kv -H "Authorization: bearer $( oc whoami --show-token )"
    "https://prometheus-k8s-openshift-monitoring.apps.migcluster.lab.rdu2.cee.redhat.com:443
    /api/v1/label/__name__/values"

    Job Query:
    curl -kv -H "Authorization: bearer $( oc whoami --show-token )"
    "https://prometheus-k8s-openshift-monitoring.apps.migcluster.lab.rdu2.cee.redhat.com:443
    /api/v1/label/job/values"

    Stats Query :
    curl -kv -H "Authorization: bearer $( oc whoami --show-token )"
    "https://prometheus-k8s-openshift-monitoring.apps.migcluster.lab.rdu2.cee.redhat.com:443
    /api/v1/query?query=instance:node_cpu_utilisation:rate1m"
"""


class OcpPrometheusClient(OcpBase):
    """
    OcpPrometheusClient extends OcpBase class and provide connection to openshift prometheus
    instance to retrieve stats from prometheus.
    :param kube_config_file: A kubernetes config file.
    """

    def __init__(self, kube_config_file=None):
        super(OcpPrometheusClient, self).__init__(kube_config_file=kube_config_file)
        self.ocp_route = OcpRoutes(kube_config_file=kube_config_file)
        self.ocp_secret = OcpSecret(kube_config_file=kube_config_file)
        self._prometheus_cache = dict()

    def get_prometheus_url(self):
        """
        Get prometheus route/url
        :return: prometheus_url (str) on success
        """
        if "prometheus_url" in self._prometheus_cache:
            return self._prometheus_cache.get("prometheus_url")
        prometheus_route = self.ocp_route.get_route_in_namespace(
            namespace="openshift-monitoring", route_name="prometheus-k8s"
        )
        prometheus_url = "https://" + prometheus_route + ":443/api"
        self._prometheus_cache.update({"prometheus_url": prometheus_url})
        logger.info("Prometheus URL : %s", prometheus_url)

        return prometheus_url

    def get_prometheus_bearer_token(self):
        """
        Get bearer token for prometheus from prometheus-k8s service account in
        "openshift-monitoring" namespace
        :return: bearer_token(str) on success
        """
        if "bearer_token" in self._prometheus_cache:
            return self._prometheus_cache.get("bearer_token")

        bearer_token = self.ocp_secret.get_long_live_bearer_token(
            sub_string="prometheus-k8s-token", namespace="openshift-monitoring"
        )
        self._prometheus_cache.update({"bearer_token": bearer_token})

        return bearer_token

    def connect_and_collect_stats(self, api_path=None, query_param=None):
        """
        Get openshift cluster statistics from openshift prometheus using prometheus rest api and python request module
        https://prometheus.io/docs/prometheus/latest/querying/api/

        :param api_path: (str) prometheus api path
        :param query_param: (str) query parameter
        :return: (dict) prometheus_api_response on success or None on Failure
        """
        prometheus_api_response = None
        prometheus_url = self.get_prometheus_url()
        bearer_token = self.get_prometheus_bearer_token()
        headers = {"Authorization": "Bearer " + bearer_token}
        final_prometheus_url = prometheus_url + api_path
        try:
            if query_param:
                params = {"query": query_param}
                # Suppress only the single warning from urllib3 needed.
                requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
                prometheus_api_response = requests.get(
                    final_prometheus_url, headers=headers, params=params, verify=False
                )
            else:
                # Suppress only the single warning from urllib3 needed.
                requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
                prometheus_api_response = requests.get(final_prometheus_url, headers=headers, verify=False)
        except (ConnectionError, HTTPError, RequestException):
            logger.exception(
                "Failed to connect %s due to refused connection or unsuccessful status code", final_prometheus_url
            )

        return prometheus_api_response.json()
