# # TODO: instead of statically doing the imports
# #       Write a method that discovers the subclasses
# #       and imports them automatically
from .ocp_base import OcpBase
from .ocp_nodes import OcpNodes
from .ocp_projects import OcpProjects
from .ocp_templates import OcpTemplates
from .ocp_apps import OcpApps
from .ocp_deploymentconfigs import OcpDeploymentconfigs
from .ocp_pods import OcpPods
from .ocp_events import OcpEvents

__all__ = ['OcpBase', 'OcpNodes', 'OcpProjects', 'OcpTemplates',
           'OcpApps', 'OcpDeploymentconfigs', 'OcpPods', 'OcpEvents']
