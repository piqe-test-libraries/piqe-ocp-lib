import logging
import random

import pytest

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_secrets import OcpSecret

logger = logging.getLogger(__loggername__)

five_digit_number = "".join(random.sample("0123456789", 5))
NAMESPACE = "default"
SA_TOKEN_NAME = "test-sa-token-{}".format(five_digit_number)
SA_TOKEN = (
    "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklpSjkuZXlKcGMzTWlPaUpyZFdKbGNtNWxkR1Z6TDNObGNuWnBZMlZoWT"
    "JOdmRXNTBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5dVlXMWxjM0JoWTJVaU9pSnZjR1Z1"
    "YzJocFpuUXRiV2xuY21GMGFXOXVJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpXTnlaWFF"
    "1Ym1GdFpTSTZJbTFwWnkxMGIydGxiaTF4TW5SM2NpSXNJbXQxWW1WeWJtVjBaWE11YVc4dmMyVnlkbWxqWldGalkyOTFibl"
    "F2YzJWeWRtbGpaUzFoWTJOdmRXNTBMbTVoYldVaU9pSnRhV2NpTENKcmRXSmxjbTVsZEdWekxtbHZMM05sY25acFkyVmhZM"
    "k52ZFc1MEwzTmxjblpwWTJVdFlXTmpiM1Z1ZEM1MWFXUWlPaUpqTVRaa1ltVTRPUzAwT0RSaExURXhaV0V0WVRObU55MW1Z"
    "VEUyTTJWbFlURTFPVGdpTENKemRXSWlPaUp6ZVhOMFpXMDZjMlZ5ZG1salpXRmpZMjkxYm5RNmIzQmxibk5vYVdaMExXMXB"
    "aM0poZEdsdmJqcHRhV2NpZlEucmhMTVhqT1ROWktUUFNvdy1hcEZMRDI4b3pZaFRHd1ZyeUJYU1RrS1ZqQzdhTjlKQzJCcX"
    "hSQmV1ZC1vRi1WWk9nak1XRndkdjh0QW5zanVEczMyclNUb3dPZXZYYWhIeG9sckk5TjBscGJncnF2VnJlQnZiVVNaWi0zN"
    "ThtZGVTT29raXc4bDNzRXZSamk2XzBrVHpqTG9MNDBUUkdSWVlLVmRhc2g0MTBrODNuZ2V4YWNqRFNpRjF4dFd0eTNFT2Fha"
    "zBlZW9YS0VqWFgwTk9xU3huZlVWUmRKRE44Z3pza3VKZDZFRXpWOG9HUFNiTUtCTEI3THJPQmJaNm9mVUZkVzBBMThPNGxaU"
    "HhTeUYxVmI4LVB3c0ZOeWRxcGJqdjB6R3Z4R2luWVNLOTA3RDZxX0NNLTRwbmFGa28zeERqV0twRWlPdTlLLU1DLUV0aTlaZERn"
)


@pytest.fixture(scope="session")
def ocp_secret(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpSecret(kube_config_file=kube_config_file)


class TestOcpSecrets:
    def test_create_secret(self, ocp_secret):
        sa_secret_body = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {"name": SA_TOKEN_NAME, "namespace": NAMESPACE},
            "type": "Opaque",
            "data": {
                # [!] Change saToken to contain a base64 encoded SA token with cluster-admin privileges on the remote
                # (AWS) cluster
                "saToken": SA_TOKEN
            },
        }
        secret_token_response = ocp_secret.create_secret(secret_cred_body=sa_secret_body)
        if (
            secret_token_response
            and secret_token_response["kind"] == "Secret"
            and secret_token_response["metadata"]["name"] == SA_TOKEN_NAME
        ):
            logger.info("Secret token created successfully")
        else:
            assert False, "Failed to create {} service access secret token".format(SA_TOKEN_NAME)

    def test_get_secret_token(self, ocp_secret):
        secret_token = ocp_secret.get_secret_token(secret_name=SA_TOKEN_NAME, namespace=NAMESPACE)
        logger.info("Secret Token : %s", secret_token)
        if not secret_token == SA_TOKEN:
            assert False

    def test_get_secret_names(self, ocp_secret):
        secret_name_list = ocp_secret.get_secret_names()
        logger.info("Secret names : %s ", secret_name_list)
        if not secret_name_list and len(secret_name_list) == 0:
            assert False, f"Failed to get secret name/s from {NAMESPACE} or There are no secrets available"

    def test_get_long_live_bearer_token(self, ocp_secret):
        bearer_token = ocp_secret.get_long_live_bearer_token()
        logger.info("Bearer Token : %s", bearer_token)
        if not bearer_token:
            assert False, "Failed to get bearer token from openshift secret"

    def test_get_secret(self):
        pass

    def test_delete_secret(self):
        pass
