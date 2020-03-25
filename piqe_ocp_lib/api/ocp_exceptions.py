""" Exceptions used while testing ocp cluster """


class ConfigError(Exception):
    """ Raise this Exception for configuration errors """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class ParseError(Exception):
    """ Raise this Exception for file parse errors """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class ExecutionError(Exception):
    """ Raise this Exception for command execution failures """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class OcpDeploymentConfigInvalidStateError(Exception):
    """ Raise this Exception when Deployment config in OCP Cluster is
    in invalid state """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class OcpAppNotSupportedError(Exception):
    """ Raise this Exception when deploying a template with template name
    not supported as part of ocp_app_mgmt module """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class OcpInvalidTemplateError(Exception):
    """ Raise this Exception when trying to fetch a Template from ocp
    cluster which doesn't exists as part of ocp cluster """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class OcpDeploymentConfigTerminatedError(Exception):
    """ Raise this Exception when Deployment config in OCP Cluster is
    in terminated state """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg


class OcpUnsupportedVersion(Exception):
    """ Raise this Exception when trying use functionality that is
    unsupported or out of scope of an OCP version """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg
