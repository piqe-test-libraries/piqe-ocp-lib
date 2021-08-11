import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpRoutes(OcpBase):
    """
    OcpPods Class extends OcpBase and encapsulates all methods
    related to managing Openshift pods.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "v1"
        self.kind = "Route"
        self.ocp_routes = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_route_names_and_paths_in_namespace(self, namespace):
        """
        Get route names and paths in specified namespace
        :param namespace :(str) name of namespace/project
        :return route_names :(dict) dict of app route names and their route
        """
        route_names = dict()
        try:
            api_response = self.ocp_routes.get(namespace=namespace)
        except ApiException as e:
            logger.error("Exception while getting routes: %s\n", e)

        if api_response:
            for route_item in api_response.items:
                route_names[route_item.metadata.name] = route_item.spec.host
        logger.info("Route Names : %s", route_names)
        return route_names

    def get_route_in_namespace(self, namespace, route_name):
        """
        Get route in specified namespace for specific app route name
        :param namespace :(str) name of namespace/project
        :param route_name :(str) name of app route name
        :return route(str): route name
        """
        route = None
        try:
            api_response = self.ocp_routes.get(namespace=namespace, name=route_name)
        except ApiException as e:
            logger.error("Exception while getting routes : %s\n", e)

        if api_response:
            route = api_response.spec.host
        logger.info("Route :%s ", route)
        return route

    def get_all_routes_in_namespace(self, namespace):
        """
        Get all routes in specified namespace
        :param namespace :(str) name of namespace/project
        :return routes :(list) list of route name
        """
        routes = list()
        route_names = self.get_route_names_and_paths_in_namespace(namespace)
        for route_name_key in route_names.keys():
            routes.append(self.get_route_in_namespace(namespace, route_name_key))
        logger.info("Routes : %s", routes)
        return routes
