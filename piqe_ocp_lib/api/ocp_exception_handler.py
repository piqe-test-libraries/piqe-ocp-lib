from contextlib import contextmanager
import json
import logging

from kubernetes.client.exceptions import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api import ocp_exceptions
from piqe_ocp_lib.api.constants import HttpStatusCode

logger = logging.getLogger(__loggername__)


@contextmanager
def handle_exception():
    """
    Raise and log relevant Ocp related exceptions
    """
    try:
        yield
    except ApiException as exception:

        # Parse the http response body to get relevant error message
        http_response_body = json.loads(exception.body.decode("utf-8"))
        exception_msg = http_response_body["message"]
        logger.info(exception_msg)

        if exception.status == HttpStatusCode.NotFound.value:
            raise ocp_exceptions.OcpResourceNotFoundException("Resource not found")
        if exception.status == HttpStatusCode.Conflict.value:
            raise ocp_exceptions.OcpResourceAlreadyExistsException("Resource Already Exists")
        if exception.status == HttpStatusCode.UnprocessableEntity.value:
            raise ocp_exceptions.OcpInvalidParameterException("Invalid parameter")
        else:
            logger.error(exception_msg)
            raise exception
