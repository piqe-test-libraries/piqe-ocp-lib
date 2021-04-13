import logging
import time

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


"""
This class requires an argocd operator to be installed.
This class discovers an applications that is deployed through argocd
"""


class OcpArgocdApplications(OcpBase):
    """
    OcpApplications Class extends OcpBase and encapsulates all methods
    related to openshift config maps.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super(OcpArgocdApplications, self).__init__(kube_config_file=kube_config_file)
        self.api_version = "argoproj.io/v1alpha1"
        self.kind = "Application"
        self.ocp_argocd_app = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_argocd_application(self, namespace):
        """
        Get an argocd applications in specific namespace
        :param namespace: (str) name of the namespace
        :return: api_response response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_argocd_app.get(namespace=namespace)
        except ApiException as e:
            logger.exception(f"Exception while getting argocd application : {e}\n")

        return api_response

    def get_an_argocd_application(self, name, namespace):
        """
        Get a specific argocd application in specific namespace
        :param name: (str) name of an argocd application
        :param namespace: (str) name of the namespace
        :return: api_response response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_argocd_app.get(name=name, namespace=namespace)
        except ApiException as e:
            logger.exception(f"Exception while getting argocd application : {e}\n")

        return api_response

    def get_argocd_applications_name(self, namespace):
        """
        Get names of all argocd applications from specific namespace
        :param namespace: (str) name of the namespace
        :return: List of argocd applications names on Success OR Empty list on Failure
        """
        argocd_apps_names = list()
        argocd_apps_response = self.get_argocd_application(namespace=namespace)

        if argocd_apps_response:
            for apps in argocd_apps_response.items:
                argocd_apps_names.append(apps.metadata.name)
        else:
            logger.warning(f"There are no argocd applications in {namespace} namespace")

        return argocd_apps_names

    def is_argocd_application_healthy(self, name, namespace):
        """
        Check the health of of argocd applications
        :param name: (str) name of the application
        :param namespace: (str) namespace
        :return: boolean
        """
        is_healthy = False
        count = 10
        while count > 0:
            app_response = self.get_an_argocd_application(name=name, namespace=namespace)
            if app_response and app_response.status:
                if app_response.status.operationState.phase == "Succeeded":
                    app_health_status = app_response.status.health.status
                    if app_health_status == "Healthy":
                        is_healthy = True
                    return is_healthy
                else:
                    # Wait for application to deploy or argocd might be syncing the apps
                    count -= 1
                    logger.info("Wait for 30 secs...")
                    time.sleep(30)

        return is_healthy

    def delete_argocd_application(self, name, namespace):
        """
        Delete a specified argocd application from specified namespace
        :param name: (str) name of ConfigMaps
        :param namespace: (str) name of namespace where ConfigMaps was created
        :return: Delete response on success OR None on Failure

        ResourceInstance[Status]:
          apiVersion: argoproj.io/v1alpha1
          details:
            kind: Application
            name: test
            uid: aa1a8359-42b0-45f9-b44b-cd0ecbff6ef8
          kind: Status
          metadata: {}
          status: Success

        """
        api_response = None
        try:
            api_response = self.ocp_argocd_app.delete(name, namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting {name} argocd application: {e}\n")
        return api_response
