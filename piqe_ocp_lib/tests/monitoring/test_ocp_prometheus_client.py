import logging

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.monitoring.ocp_prometheus_client import OcpPrometheusClient

logger = logging.getLogger(__loggername__)


@pytest.fixture(scope="session")
def ocp_prometheus_client(get_kubeconfig):
    return OcpPrometheusClient(kube_config_file=get_kubeconfig)


class TestOcpPrometheusClient:
    def test_get_prometheus_url(self, ocp_prometheus_client):
        logger.info("Get prometheus URL")
        prometheus_url = ocp_prometheus_client.get_prometheus_url()
        assert isinstance(prometheus_url, str)
        if not prometheus_url:
            assert False, "Failed to get prometheus URL"

    def test_get_prometheus_bearer_token(self, ocp_prometheus_client):
        logger.info("Get prometheus bearer token")
        prom_bearer_token = ocp_prometheus_client.get_prometheus_bearer_token()
        assert isinstance(prom_bearer_token, str)
        if not prom_bearer_token:
            assert False, "Failed to get prometheus bearer(secret) token"

    def test_connect_and_collect_stats(self, ocp_prometheus_client):
        logger.info("Connect and collect the stats from openshift prometheus")
        api_path = "/v1/label/job/values"
        prom_response = ocp_prometheus_client.connect_and_collect_stats(api_path=api_path)
        assert isinstance(prom_response, dict)
        if not prom_response and len(prom_response["data"]["result"]) == 0:
            assert False, f"Failed to retrieve the response for {api_path} api"
