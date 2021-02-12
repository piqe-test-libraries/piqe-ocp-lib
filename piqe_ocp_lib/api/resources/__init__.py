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
from .ocp_secrets import OcpSecret
from .ocp_routes import OcpRoutes
from .ocp_cluster_operators import OcpClusterOperator
from .ocp_control_planes import OcpControlPlane
from .ocp_cluster_versions import OcpClusterVersion
from .ocp_configs import OcpConfig
from .ocp_limit_ranges import OcpLimitRanges

__all__ = ['OcpBase', 'OcpNodes', 'OcpProjects', 'OcpTemplates', 'OcpRoutes',
           'OcpApps', 'OcpDeploymentconfigs', 'OcpPods', 'OcpEvents', 'OcpSecret',
           'OcpClusterOperator', 'OcpControlPlane', 'OcpClusterVersion', 'OcpConfig', 'OcpLimitRanges']
