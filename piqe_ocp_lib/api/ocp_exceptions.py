""" Exceptions used while testing ocp cluster """


class ConfigError(Exception):
    """ Raise this Exception for configuration errors """

    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class ExecutionError(Exception):
    """ Raise this Exception for command execution failures """

    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class OcpException(Exception):
    """Base exception class for Ocp Api exceptions"""

    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class OcpResourceAlreadyExistsException(OcpException):
    """Raise this Exception when trying to access a resource
    that already exists"""

    pass


class OcpResourceNotFoundException(OcpException):
    """Raise this Exception when trying to access a resource
    which does not exist"""

    pass


class OcpInvalidParameterException(OcpException):
    """Raise this Exception when trying to access a resource
    which does not exist"""

    pass


class OcpWatchTimeoutException(OcpException):
    """Raise this Exception after timeout while watching a Ocp
    resource"""

    pass


class OcpServiceUnavailable(OcpException):
    """Raise this Exception when trying to access unavailable
    service"""

    pass


class OcpDeploymentConfigInvalidStateError(OcpException):
    """Raise this Exception when Deployment config in OCP Cluster is
    in invalid state"""

    pass


class UnsupportedInstallMode(OcpException):
    """Raise this Exception when trying to install an operator
    with an unsupported install mode"""

    pass
