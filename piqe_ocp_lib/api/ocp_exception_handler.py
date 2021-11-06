import functools
import json
import logging

from kubernetes.client.exceptions import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api import ocp_exceptions
from piqe_ocp_lib.api.constants import HttpStatusCode

logger = logging.getLogger(__loggername__)


def get_error_msg(exception) -> str:
    """
    Parse the http response body to get relevant error message
    """
    http_response_body = json.loads(exception.body.decode("utf-8"))
    exception_msg = http_response_body["message"]
    return exception_msg


def handle_exception(func):
    """
    Raise and log relevant Ocp related exceptions
    """

    @functools.wraps(func)
    def exception_handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiException as exception:
            logger.info(get_error_msg(exception))
            if exception.status == HttpStatusCode.NotFound.value:
                raise ocp_exceptions.OcpResourceNotFoundException("Resource not found")
            if exception.status == HttpStatusCode.Conflict.value:
                raise ocp_exceptions.OcpResourceAlreadyExistsException("Resource Already Exists")
            if exception.status == HttpStatusCode.UnprocessableEntity.value:
                raise ocp_exceptions.OcpInvalidParameterException("Invalid parameter")
            else:
                logger.error(get_error_msg(exception))
                raise exception

    return exception_handler
