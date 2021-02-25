import logging
import pytest
import random
from piqe_ocp_lib.api.resources import OcpLimitRanges
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)

five_digit_number = ''.join(random.sample('0123456789', 5))
NAMESPACE = "default"
NAME = "test{five_digit_number}"


@pytest.fixture(scope="session")
def ocp_lr(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpLimitRanges(kube_config_file=kube_config_file)


@pytest.fixture(scope="session")
def lr_body():
    lr_body = {
        "kind": "LimitRange",
        "apiVersion": "v1",
        "metadata": {
            "name": NAME,
            "namespace": NAMESPACE,
        },
        "spec": {
            "limits": [
                {
                    "type": "Container",
                    "max": {"cpu": "1200M",
                            "memory": "1Gi"},
                    "min": {"memory": "528Mi",
                            "cpu": "200M"}
                }

            ]
        }

    }

    return lr_body


class TestOcpLimitRanges:

    def test_container_limit_range_item_builder(self, ocp_lr):
        logger.info("Create a Container V1LimitRangeItem")
        lr_item = ocp_lr.container_limit_range_item().memory(min="512Mb", max="1G").cpu(min="200M").build()
        logger.info(f"Create Response : {lr_item}")
        if not lr_item.min.get('memory') == '512Mb' and \
                not lr_item.type == 'Container':
            assert False, "Failed to create Container V1LimitRangeItem"

    def test_pod_limit_range_item_builder(self, ocp_lr):
        logger.info("Create a Pod V1LimitRangeItem")
        lr_item = ocp_lr.pod_limit_range_item().memory(min="512Mb", max="1G").cpu(min="200M").build()
        logger.info(f"Create Response : {lr_item}")
        if not lr_item.min.get('cpu') == '200M' and \
                not lr_item.type == 'Pod':
            assert False, "Failed to create Pod V1LimitRangeItem"

    def test_image_limit_range_item_builder(self, ocp_lr):
        logger.info("Create a Image V1LimitRangeItem")
        lr_item = ocp_lr.image_limit_range_item().storage(max="1G").build()
        logger.info(f"Create Response : {lr_item}")
        if not lr_item.max.get('storage') == '1G' and \
                not lr_item.type == 'openshift.io/Image':
            assert False, "Failed to create Image V1LimitRangeItem"

    def test_image_stream_limit_range_item_builder(self, ocp_lr):
        logger.info("Create a ImageStream V1LimitRangeItem")
        lr_item = ocp_lr.image_stream_limit_range_item().images(max="10").build()
        logger.info(f"Create Response : {lr_item}")
        if not lr_item.max.get('images') == '10' and \
                not lr_item.type == 'openshift.io/ImageStream':
            assert False, "Failed to create ImageStream V1LimitRangeItem"

    def test_persistent_volume_claim_limit_range_item_builder(self, ocp_lr):
        logger.info("Create a PersistentVolumeClaim V1LimitRangeItem")
        lr_item = ocp_lr.persistent_volume_claim_limit_range_item().storage(max="10G").build()
        logger.info(f"Create Response : {lr_item}")
        if not lr_item.max.get('storage') == '10G' and \
                not lr_item.type == 'PersistentVolumeClaim':
            assert False, "Failed to create PersistentVolumeClaim V1LimitRangeItem"

    def test_build_limit_range(self, ocp_lr):
        logger.info("Building a V1LimitRange")
        lris = list()
        lris.append(ocp_lr.container_limit_range_item().memory(min="512Mb", max="1G").cpu(min="200M").build())
        lris.append(ocp_lr.persistent_volume_claim_limit_range_item().storage(max="10G").build())
        lr = ocp_lr.build_limit_range(name=NAME, namespace=NAMESPACE, item_list=lris)
        logger.info(f"Create Response : {lr}")
        if not isinstance(lr.spec.limits, list) and \
                len(lr.spec.limits) != 2:
            assert False, "Failed to build a V1LimitRange"

    def test_build_two_limit_range_items_not_equal(self, ocp_lr):
        logger.info("Creating two V1LimitRangeItems")
        clr1 = ocp_lr.container_limit_range_item().memory(min="512Mb", max="1G").cpu(min="200M").build()
        clr2 = ocp_lr.container_limit_range_item().memory(max="10G").build()

        if not (clr1 != clr2):
            assert False, "Failed to create two different V1LimitRangeItems"

    def test_create_limit_range(self, ocp_lr):
        logger.info(f"Create a {NAME} LimitRanges in {NAMESPACE} namespace")
        lrl = list()
        lrl.append(ocp_lr.container_limit_range_item().cpu(min="200M", max="1200M").memory(min="528Mi",
                                                                                           max="1Gi").build())
        lrl.append(ocp_lr.persistent_volume_claim_limit_range_item().storage(max="10G").build())
        lr_body = ocp_lr.build_limit_range(name=NAME, namespace=NAMESPACE, item_list=lrl)
        create_lr_response = ocp_lr.create_a_limit_range(limit_ranges_body=lr_body)
        logger.info(f"Create Response : {create_lr_response}")
        if not create_lr_response.metadata.name == NAME and \
                not create_lr_response.metadata.namespace == NAMESPACE:
            assert False, f"Failed to create {NAME} LimitRange in {NAMESPACE} namespace"

    def test_get_limit_ranges(self, ocp_lr):
        logger.info("Get limit ranges")
        lr_response = ocp_lr.get_limit_ranges(namespace=NAMESPACE)
        if not lr_response and len(lr_response.items) <= 0:
            assert False, "Failed to get LimitRanges"

    def test_get_a_limit_range(self, ocp_lr):
        logger.info(f"Get a {NAME} limit range")
        a_lr_response = ocp_lr.get_a_limit_range(name=NAME, namespace=NAMESPACE)
        if not a_lr_response:
            assert False, f"Failed to get {NAME} LimitRange"

    def test_get_limit_ranges_names(self, ocp_lr):
        logger.info("Get names of all limit ranges from specified namespace")
        lr_names = ocp_lr.get_limit_ranges_names(namespace=NAMESPACE)
        if not lr_names and len(lr_names) <= 0:
            assert False, f"Failed to get LimitRanges names in {NAMESPACE} namespace"

    def test_update_limit_range(self, ocp_lr):
        logger.info("Patch a limit range from specified namespace")
        patch_set = [
            {
                "type": "Container",
                "max": {"cpu": "1200M",
                        "memory": "1Gi"},
                "min": {"memory": "528Mi",
                        "cpu": "400M"}
            },
            {
                "type": "PersistentVolumeClaim",
                "max": {"storage": "10G"}
            }

        ]
        lr_resp = ocp_lr.update_a_limit_range(namespace=NAMESPACE, name=NAME, item_list=patch_set)
        logger.info(f"Patch Response : {lr_resp}")
        assert lr_resp.spec.limits[0].min.cpu == '400M'

    def test_replace_limit_range(self, ocp_lr, lr_body):
        logger.info("replace the LimitRange from specified namespace")
        lr_body.get('spec').get('limits').append({
            "type": "Pod",
            "max": {"cpu": "1200M",
                    "memory": "1Gi"},
        })
        lr_resp = ocp_lr.replace_a_limit_range(limit_range_body=lr_body)
        if not lr_resp and len(lr_resp.items) <= 0:
            assert False, f"Failed to replace LimitRange in {NAMESPACE} namespace"
        assert lr_resp.spec.limits[-1].type == 'Pod'

    def test_delete_a_limit_range(self, ocp_lr):
        logger.info(f"Delete a {NAME} LimitRange")
        delete_lr_response = ocp_lr.delete_a_limit_range(name=NAME, namespace=NAMESPACE)
        logger.info(f"Delete Response : {delete_lr_response}")
        if not delete_lr_response and delete_lr_response["status"] != "Success":
            assert False, f"Failed to delete {NAME} LimitRange in {NAMESPACE} namespace"
