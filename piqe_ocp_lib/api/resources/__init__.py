# # TODO: instead of statically doing the imports
# #       Write a method that discovers the subclasses
# #       and imports them automatically
from .ocp_apps import OcpApps
from .ocp_base import OcpBase
from .ocp_cluster_operators import OcpClusterOperator
from .ocp_cluster_versions import OcpClusterVersion
from .ocp_configs import OcpConfig
from .ocp_control_planes import OcpControlPlane
from .ocp_deploymentconfigs import OcpDeploymentconfigs
from .ocp_events import OcpEvents
from .ocp_limit_ranges import OcpLimitRanges
from .ocp_machine_management import OcpMachineHealthCheck, OcpMachines, OcpMachineSet
from .ocp_nodes import OcpNodes
from .ocp_pods import OcpPods
from .ocp_projects import OcpProjects
from .ocp_resource_quotas import OcpResourceQuota
from .ocp_routes import OcpRoutes
from .ocp_secrets import OcpSecret
from .ocp_services import OcpServices
from .ocp_templates import OcpTemplates
from .ocp_virtual_machine import OcpVirtualMachines, VirtualMachine

__all__ = [
    "OcpBase",
    "OcpNodes",
    "OcpProjects",
    "OcpTemplates",
    "OcpRoutes",
    "OcpApps",
    "OcpDeploymentconfigs",
    "OcpPods",
    "OcpEvents",
    "OcpSecret",
    "OcpClusterOperator",
    "OcpControlPlane",
    "OcpClusterVersion",
    "OcpConfig",
    "OcpLimitRanges",
    "OcpMachineSet",
    "OcpMachines",
    "OcpServices",
    "OcpVirtualMachines",
    "VirtualMachine",
    "OcpResourceQuota",
    "OcpMachineHealthCheck",
]
