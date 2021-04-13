import logging

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.monitoring.ocp_cluster_stats_prometheus import OcpClusterStatsPrometheus

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="session")
def ocp_cluster_stats_prom(get_kubeconfig):
    return OcpClusterStatsPrometheus(kube_config_file=get_kubeconfig)


class TestOcpClusterStatsPrometheus:
    def test_get_prometheus_labels(self, ocp_cluster_stats_prom):
        logger.info("Get prometheus labels")
        prometheus_labels = ocp_cluster_stats_prom.get_prometheus_ocp_labels()
        assert isinstance(prometheus_labels, list)
        if not prometheus_labels and len(prometheus_labels) == 0:
            assert False, "Failed to get prometheus openshift labels"

    def test_get_prometheus_jobs(self, ocp_cluster_stats_prom):
        logger.info("Get prometheus jobs labels")
        prometheus_ocp_jobs = ocp_cluster_stats_prom.get_prometheus_ocp_jobs()
        assert isinstance(prometheus_ocp_jobs, list)
        if not prometheus_ocp_jobs and len(prometheus_ocp_jobs) == 0:
            assert False, "Failed to get prometheus openshift jobs"

    def test_get_cluster_stats_using_query_param(self, ocp_cluster_stats_prom):
        logger.info("Get openshift cluster stats from prometheus")
        label = "namespace:container_cpu_usage:sum"
        cluster_stats_dict = ocp_cluster_stats_prom.get_cluster_stats_using_query_param(label=label)
        assert isinstance(cluster_stats_dict, dict)
        if not cluster_stats_dict and len(cluster_stats_dict["result"]) == 0:
            assert False, f"Failed to get cluster stats for label {label}"
