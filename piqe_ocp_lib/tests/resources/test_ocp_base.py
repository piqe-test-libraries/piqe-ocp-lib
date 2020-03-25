from piqe_ocp_lib.api.resources import OcpBase
from openshift.dynamic import DynamicClient
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class TestOcpBase(object):
    """
    1. Create an instance of OcpBase class
    2. Verify that the init returns a valid object
       that has a dynamic client object as an
       instance attribute.
    3. Verify that the instance attribute kube_config_file
       was updated and is not None.
    4. Check version to be a three element tuple (Semantic Versioning) and that
       each of the elements is of type string.
    """
    def test_init(self, get_kubeconfig):
        base_api_obj = OcpBase(kube_config_file=get_kubeconfig)
        assert isinstance(base_api_obj.dyn_client, DynamicClient)
        assert base_api_obj.kube_config_file is not None
        major, minor, patch = base_api_obj.version()
        logger.info("The obtained version is: {}.{}.{}".format(major, minor, patch))
        assert isinstance(base_api_obj.version(), tuple)
        assert len(base_api_obj.version()) == 3
        assert isinstance(major, str) and isinstance(minor, str) and isinstance(patch, str)
