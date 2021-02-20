import logging
import random

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources import OcpResourceQuota

logger = logging.getLogger(__loggername__)

five_digit_number = "".join(random.sample("0123456789", 5))
NAMESPACE = "default"
NAME = f"test{five_digit_number}"


@pytest.fixture(scope="session")
def ocp_rq(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpResourceQuota(kube_config_file=kube_config_file)


@pytest.fixture(scope="session")
def rq_body():
    rq_body = {
        "kind": "ResourceQuota",
        "apiVersion": "v1",
        "metadata": {
            "name": NAME,
            "namespace": NAMESPACE,
        },
        "spec": {
            "hard": {"requests.cpu": "400M", "requests.memory": "512Mi", "pods": "4"},
            "scopes": ["NotTerminating", "NotBestEffort"],
        },
    }

    return rq_body


class TestOcpResourceQuotas:
    def test_compute_resource_quota_spec_builder(self, ocp_rq):
        logger.info("Create a compute V1ResourceQuotaSpec")
        rq_item = (
            ocp_rq.resource_quota_spec().memory(requests="512Mi").cpu(requests="1200M").terminating_scope().build()
        )
        logger.info(f"Create Response : {rq_item}")
        if not rq_item.hard.get("memory") == "512Mb" and len(rq_item.scopes) != 1:
            assert False, "Failed to create compute V1ResourceQuotaSpec"

    def test_object_count_resource_quota_spec_builder(self, ocp_rq):
        logger.info("Create an object count V1ResourceQuotaSpec")
        rq_item = ocp_rq.resource_quota_spec().persistent_volume_claims(count="8").build()
        logger.info(f"Create Response : {rq_item}")
        if not rq_item.hard.get("persistentvolumeclaims") == "8":
            assert False, "Failed to create object count V1ResourceQuotaSpec"

    def test_storage_resource_quota_spec_builder(self, ocp_rq):
        logger.info("Create a storage V1ResourceQuotaSpec")
        rq_item = (
            ocp_rq.resource_quota_spec()
            .ephemeral_storage(requests="1G")
            .storage_class(class_name="gold", requests="8G")
            .build()
        )
        logger.info(f"Create Response : {rq_item}")
        if (
            not rq_item.hard.get("requests.ephemeral-storage") == "1G"
            and not rq_item.hard.get("gold.storageclass.storage.k8s.io/requests.storage") == "8G"
        ):
            assert False, "Failed to create storage V1ResourceQuotaSpec"

    def test_selector_expression_resource_quota_spec_builder(self, ocp_rq):
        logger.info("Create a PriorityClass V1ScopedResourceSelectorRequirement")
        rq_item = (
            ocp_rq.resource_quota_spec()
            .scope_selector()
            .priority_class_scope()
            .in_()
            .values(vals=["high"])
            .done()
            .build()
        )
        logger.info(f"Create Response : {rq_item}")
        if (
            not rq_item.scope_selector.match_expressions[-1].operator == "In"
            and len(rq_item.scope_selector.match_expressions[-1].values) != 1
        ):
            assert False, "Failed to create a priority class V1ResourceQuotaSpec"

    def test_selector_expression_resource_quota_spec_rule_check(self, ocp_rq):
        logger.info("Create a V1ScopedResourceSelectorRequirement")
        with pytest.raises(Exception):
            ocp_rq.resource_quota_spec().scope_selector().terminating_scope().not_exists().done().build()

    def test_extended_resource_quota_spec_builder(self, ocp_rq):
        logger.info("Create an extended resource V1ResourceQuotaSpec")
        rq_item = ocp_rq.resource_quota_spec().resource(resource="nvidia.com/gpu", requests="4").build()
        logger.info(f"Create Response : {rq_item}")
        if "requests.nvidia.com/gpu" not in rq_item.hard and not rq_item.hard.get("requests.nvidia.com/gpu") == "4":
            assert False, "Failed to create extended resource V1ResourceQuotaSpec"

    def test_extended_resource_count_spec_builder(self, ocp_rq):
        logger.info("Create a standard resource count V1ResourceQuotaSpec")
        rq_item = ocp_rq.resource_quota_spec().resource(resource="deployments.apps", count="4").build()
        logger.info(f"Create Response : {rq_item}")
        if "count/deployments.apps" not in rq_item.hard and not rq_item.hard.get("count/deployments.apps") == "4":
            assert False, "Failed to create standard resource count V1ResourceQuotaSpec"

    def test_create_resource_quota(self, ocp_rq):
        logger.info(f"Create a {NAME} ResourceQuota in {NAMESPACE} namespace")
        spec = (
            ocp_rq.resource_quota_spec()
            .memory(requests="512Mi")
            .cpu(requests="1200M")
            .pods(count="5")
            .not_terminating_scope()
            .not_best_effort_scope()
            .build()
        )
        rq_body = ocp_rq.resource_quota(name=NAME, namespace=NAMESPACE, spec=spec)
        create_rq_response = ocp_rq.create_a_resource_quota(resource_quota_body=rq_body)
        logger.info(f"Create Response:\n{create_rq_response}")
        if not create_rq_response.metadata.name == NAME and not create_rq_response.metadata.namespace == NAMESPACE:
            assert False, f"Failed to create {NAME} ResourceQuota in {NAMESPACE} namespace"

    def test_get_resource_quotas(self, ocp_rq):
        logger.info("Get resource quotas")
        rq_response = ocp_rq.get_resource_quotas(namespace=NAMESPACE)
        logger.info(f"Get Response:\n{rq_response}")
        if not rq_response and len(rq_response.items) <= 0:
            assert False, "Failed to get resource quotas"

    def test_get_a_resource_quota(self, ocp_rq):
        logger.info(f"Get a {NAME} resource quota")
        a_rq_response = ocp_rq.get_a_resource_quota(name=NAME, namespace=NAMESPACE)
        logger.info(f"Get Response:\n{a_rq_response}")
        if not a_rq_response:
            assert False, f"Failed to get {NAME} ResourceQuota"

    def test_get_a_resource_quota_status(self, ocp_rq):
        logger.info(f"Get a {NAME} resource quota status")
        a_rq_response = ocp_rq.get_a_resource_quota_status(name=NAME, namespace=NAMESPACE)
        logger.info(f"Status Response:\n{a_rq_response.used}")
        if not a_rq_response and not (hasattr(a_rq_response, "used") or hasattr(a_rq_response, "hard")):
            assert False, f"Failed to get {NAME} ResourceQuotaStatus"

    def test_get_resource_quota_names(self, ocp_rq):
        logger.info("Get names of all resource quotas from specified namespace")
        lr_names = ocp_rq.get_resource_quotas_names(namespace=NAMESPACE)
        if not lr_names and len(lr_names) <= 0:
            assert False, f"Failed to get ResourceQuota names in {NAMESPACE} namespace"

    def test_update_resource_quota(self, ocp_rq):
        logger.info("Patch a resource quota from specified namespace")
        patch_set = {
            "hard": {"requests.cpu": "1200M", "requests.memory": "1Gi", "pods": "4"},
            "scopes": ["NotTerminating", "NotBestEffort"],
        }
        lr_resp = ocp_rq.update_a_resource_quota(namespace=NAMESPACE, name=NAME, spec=patch_set)
        logger.info(f"Patch Response:\n{lr_resp}")
        assert lr_resp.spec.hard.pods == "4"

    def test_replace_resource_quota(self, ocp_rq, rq_body):

        logger.info("replace the ResourceQuota from specified namespace")
        lr_resp = ocp_rq.replace_a_resource_quota(resource_quota_body=rq_body)
        if not lr_resp and len(lr_resp.items) <= 0:
            assert False, f"Failed to replace ResourceQuota in {NAMESPACE} namespace"
        assert len(lr_resp.spec.scopes) == 2

    def test_delete_a_resource_quota(self, ocp_rq):
        logger.info(f"Delete a {NAME} ResourceQuota")
        delete_rq_response = ocp_rq.delete_a_resource_quota(name=NAME, namespace=NAMESPACE)
        logger.info(f"Delete Response : \n{delete_rq_response}")
        if not delete_rq_response and delete_rq_response["status"] != "Success":
            assert False, f"Failed to delete {NAME} ResourceQuota in {NAMESPACE} namespace"
