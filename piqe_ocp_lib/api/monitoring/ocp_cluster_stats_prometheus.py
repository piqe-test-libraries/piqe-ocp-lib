import logging
from piqe_ocp_lib.api.monitoring.ocp_prometheus_client import OcpPrometheusClient
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpClusterStatsPrometheus:
    def __init__(self, kube_config_file=None):
        """
        This class used ocp_prometheus_client.py class to connect and collect stats from prometheus.
        """
        self.prometheus_client = OcpPrometheusClient(kube_config_file=kube_config_file)

    def get_prometheus_ocp_labels(self):
        """
        Get openshift stats labels from prometheus
        :return: (list) List of prometheus_labels
        """
        api_path = "/v1/label/__name__/values"
        api_response = self.prometheus_client.connect_and_collect_stats(api_path=api_path)
        prometheus_labels = api_response.get("data")

        return prometheus_labels

    def get_prometheus_ocp_jobs(self):
        """
        Get openshift jobs name from prometheus
        :return: (list) List of prometheus_jobs
        """
        api_path = "/v1/label/job/values"
        api_response = self.prometheus_client.connect_and_collect_stats(api_path=api_path)
        prometheus_jobs = api_response.get("data")

        return prometheus_jobs

    def get_cluster_stats_using_query_param(self, label=None):
        """
        Get cluster stats from prometheus using query parameter
        :param label: (str) prometheus label
        :return: (dict) prometheus_data on success or None on failure
        """
        prometheus_data = None
        api_path = "/v1/query"
        api_response = self.prometheus_client.connect_and_collect_stats(api_path=api_path, query_param=label)
        logger.info("Query Response for label %s\n : %s", label, api_response)
        if api_response["status"] == "success":
            prometheus_data = api_response.get("data")

        return prometheus_data
