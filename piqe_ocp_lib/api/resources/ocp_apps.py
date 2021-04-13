import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__

from .ocp_base import OcpBase
from .ocp_templates import OcpTemplates

logger = logging.getLogger(__loggername__)


class OcpApps(OcpBase):
    """
    OcpApps Class extends OcpBase and encapsulates all methods
    related to managing Openshift app deployment.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        self.kube_config_file = kube_config_file
        OcpBase.__init__(self, kube_config_file=self.kube_config_file)
        self.ocp_template_obj = OcpTemplates(kube_config_file=self.kube_config_file)

    def create_app_from_template(self, project, template_name, ident, app_params, template_location="openshift"):
        """
        This method fetches a raw template by name, enumerates it,
        processes it and uses it to deploy an app in a specified
        project. project and template_name params are of type
        string while ident is of type int
        :param project: (required | str) The project that will host the app
        :param template_name: (required | str) The template to be used to deploy the app
        :param ident: (required | int) Unique identifier.
        :param app_params (required | dict) app param for ocp app
        :return: A list of response objects obtained from the deployment of every
                 resource in this app. Also a list of the deployment configs
                 that are part of this app.
        """
        # A list to store all the response objects of our deployment
        api_response_list = list()
        # Fetch a raw template
        unprocessed_template = self.ocp_template_obj.get_a_template_in_a_namespace(
            template_name, project=template_location
        )
        # Enumerate it to ensure uniqueness
        enumerated_unprocessed_template = self.ocp_template_obj.enumerate_unprocessed_template(
            unprocessed_template, ident, app_params
        )
        # Process it so it's ready to use for deploying an app
        processed_template = self.ocp_template_obj.create_a_processed_template(enumerated_unprocessed_template)
        # Apps can have multiple deployment configs. it is based on their status that we determine
        # whether an app is ready or not so we create a list where we will compile the names of
        # deployment configs present in this app.
        deployment_config_names = []
        # We iterate through all the resources that make this app so we can
        # deploy them one by one.
        for resource in processed_template["objects"]:
            if resource["kind"] == "DeploymentConfig":
                deployment_config_names.append(resource["metadata"]["name"])
            try:
                current_resource = self.dyn_client.resources.get(
                    api_version=resource["apiVersion"], kind=resource["kind"]
                )
                api_response = current_resource.create(body=resource, namespace=project)
                api_response_list.append(api_response)
            except ApiException as e:
                logger.error(
                    "Exception when calling method: "
                    " create_app_from_template_" + str(resource["kind"]).lower() + "%s\n",
                    e,
                )
        return api_response_list, deployment_config_names

    def delete_template_based_app(self, project, template_name, ident, app_params, template_location="openshift"):
        """
        A method to delete a template based app. Loops through the objects
        list in the app template and deletes resources bases on their kind.
        :param project: The project containing the targeted app. Of type str
        :param template_name: The app template corresponding to the targeted app. Of type str
        :param ident: The unique identifier to be appended to the resource names
                      to ensure its uniqueness within a project. Of Type int.
        :param app_params (required | int) app param for ocp app
        :return: A list of response objects obtained from the deletion of every
                 resource in this app.
        """
        # A list to store all the response objects resulting from the deletion
        # of an app
        api_response_list = list()
        # Fetch the app template, enumerate it and process it so we can obtain the correct names
        # of the resources that need to be deleted.
        unprocessed_template = self.ocp_template_obj.get_a_template_in_a_namespace(
            template_name, project=template_location
        )
        enumerated_unprocessed_template = self.ocp_template_obj.enumerate_unprocessed_template(
            unprocessed_template, ident, app_params
        )
        processed_template = self.ocp_template_obj.create_a_processed_template(enumerated_unprocessed_template)
        # Loop through the name of every resouce defined in the processed template and delete it.
        for resource in processed_template["objects"]:
            try:
                current_resource = self.dyn_client.resources.get(
                    api_version=resource["apiVersion"], kind=resource["kind"]
                )
                api_response = current_resource.delete(name=resource["metadata"]["name"], namespace=project)
                api_response_list.append(api_response)
            except ApiException as e:
                logger.error(
                    "Exception when calling method: "
                    " delete_template_based_app_" + str(resource["kind"]).lower() + "%s\n",
                    e,
                )
        return api_response_list
