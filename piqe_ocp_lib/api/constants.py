import os
from enum import Enum

CLUSTER_VERSION_OPERATOR_ID: str = "version"
CLUSTER_POLLING_SECONDS_INTERVAL: int = os.environ.get("CLUSTER_POLLING_SECONDS_INTERVAL", 120)

class HttpStatusCode(Enum):
    OK = 200
    Accepted = 202
    BadRequest = 400
    Conflict = 409
    NotFound = 404
    ServiceUnavailable = 503