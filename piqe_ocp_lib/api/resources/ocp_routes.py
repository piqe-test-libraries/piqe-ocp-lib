from css_openshift.lib.ocpmgmt.ocp_base import OcpBase
from kubernetes.client.rest import ApiException
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpRoutes(OcpBase):
    """
    OcpPods Class extends OcpBase and encapsulates all methods
    related to managing Openshift pods.
    :param hostname: (optional | str) The hostname/FQDN/IP of the master
                     node of the targeted OCP cluster. Defaults to
                     localhost if unspecified.
    :param username: (optional | str) login username. Defaults to admin
                      if unspecified.
    :param password: (optional | str) login password. Defaults to redhat
                      if unspecified.
    :param kube_config_file: A kubernetes config file. It overrides
                             the hostname/username/password params
                             if specified.
    :return: None
    """
    def __init__(self, hostname='localhost', username='admin', password='redhat', kube_config_file=None):
        super(OcpRoutes, self).__init__(hostname, username, password, kube_config_file)
        self.api_version = 'v1'
        self.kind = 'Route'
        self.ocp_routes = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)
    """
        Get route names and paths in specified namespace
        :param namespace(str): name of namespace/project
        :return route_names (dict): dict of app route names and their route
    """
    def get_route_names_and_paths_in_namespace(self, namespace):
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

    """
        Get route in specified namespace for specific app route name
        :param namespace(str): name of namespace/project
        :param route_name(str): name of app route name
        :return route(str): route name
    """
    def get_route_in_namespace(self, namespace, route_name):
        route = None
        try:
            api_response = self.ocp_routes.get(namespace=namespace, name=route_name)
        except ApiException as e:
            logger.error("Exception while getting routes : %s\n", e)

        if api_response:
            route = api_response.spec.host
        logger.info("Route :%s ", route)
        return route

    """
        Get all routes in specified namespace
        :param namespace(str): name of namespace/project
        :return routes(list): list of route name
    """
    def get_all_routes_in_namespace(self, namespace):
        routes = list()
        route_names = self.self.get_route_names_and_paths_in_namespace(namespace)
        for route_name_key in route_names.keys():
            routes.append(self.get_route_in_namespace(namespace, route_name_key))
        logger.info("Routes : %s", routes)
        return routes
