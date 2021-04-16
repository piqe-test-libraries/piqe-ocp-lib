import jmespath

from piqe_ocp_lib.api.resources import OcpBase


class OcpServices(OcpBase):
    """
    OcpServices class extends OcpBase and encapsulates all methods
    related to managing Openshift Service.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "v1"
        self.kind = "Service"
        self.svc = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_all_from_project(self, project_name: str):
        """
        Return all available services in this namespace
        """
        return self.svc.get(namespace=project_name)

    def get_app_ip(self, project_name: str, app_name: str) -> str:
        """
        Return IP of the service associated with app_name living in project_name
        """
        query = f"items[?metadata.name=='{app_name}'].spec.clusterIP | [0]"
        project_services = self.get_all_from_project(project_name)
        return jmespath.search(query, project_services.to_dict())
