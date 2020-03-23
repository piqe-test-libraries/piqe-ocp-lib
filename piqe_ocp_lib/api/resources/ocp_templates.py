from .ocp_base import OcpBase
from kubernetes.client.rest import ApiException
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpTemplates(OcpBase):
    """
    OcpTemplates Class extends OcpBase and encapsulates all methods
    related to managing Openshift templates.
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
        self.hostname = hostname
        self.username = username
        self.password = password
        self.kube_config_file = kube_config_file
        OcpBase.__init__(self, hostname=self.hostname,
                         username=self.username,
                         password=self.password,
                         kube_config_file=self.kube_config_file)
        self.api_version = 'template.openshift.io/v1'
        self.kind = 'Template'
        self.ocp_unprocessed_templates = self.dyn_client.resources.get(api_version=self.api_version,
                                                                       kind=self.kind, name='templates')
        self.ocp_processed_templates = self.dyn_client.resources.get(api_version=self.api_version,
                                                                     kind=self.kind, name='processedtemplates')
        # TODO: Instead of using this mapper dictionary, we can just pass the parameters that need to be changed as
        # key value pairs using **kwargs to the relevant methods in ocp_templates.py and ocp_apps.py
        # We might then want to provide a helper method that takes as an input a raw template and/or
        # a template name and return the list associated with the parameters key in a template.
        self.app_params_dict = {
            'jenkins-ephemeral':
                {
                    'create': ('JENKINS_SERVICE_NAME', 'JNLP_SERVICE_NAME')
                },
            'jenkins-persistent':
                {
                    'create': ('JENKINS_SERVICE_NAME', 'JNLP_SERVICE_NAME')
                },
            '128mb-fio':
                {
                    'create': ('NAME')
                },
            'httpd-example':
                {
                    'create': ('NAME')
                },
            'cakephp-mysql-example':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'dancer-mysql-example':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'django-psql-example':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'nodejs-mongodb-example':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'rails-postgresql-example':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'cakephp-mysql-persistent':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'dancer-mysql-persistent':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'django-psql-persistent':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'nodejs-mongo-persistent':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'rails-pgsql-persistent':
                {
                    'create': ('NAME', 'DATABASE_SERVICE_NAME')
                },
            'fio-persistent':
                {
                    'create': ('NAME', 'PVC_NAME')
                }
        }

    def get_a_template_in_a_namespace(self, template_name, project='openshift'):
        """
        A mtehod that fetches an unprocessed template and returns it in
        dictionary format.
        :param template_name: (required | str) The template name.
        :param namespace: (optional | str) The project where the template resides.
                           Defaults to 'openhsift' if unspecified.
        :return: A unprocessed template of type dict
        """
        api_response = None
        try:
            api_response = self.ocp_unprocessed_templates.get(name=template_name, namespace=project)
        except ApiException as e:
            logger.error("Exception when calling method create_project_request: %s\n" % e)
        if api_response:
            return api_response.to_dict()
        else:
            return api_response

    def enumerate_unprocessed_template(self, template, ident, app_params=None):
        """
        We use enumerate the minimum required parameters using the apps_param_dict attribute.
        :param template: (required | dict) An uprocessed template.
        :param ident: (required | int) Unique identifier.
        :param app_params (optional | dict) app_param for template
        :return: An enumerated templated of type dict
        """
        ret = None
        app_name = template['metadata']['name']
        if app_name not in self.app_params_dict:
            logger.warning("!!! The app %s is not currently supported, skipping ... !!!", app_name)
        else:
            for obj in template['parameters']:
                if obj['name'] in self.app_params_dict[app_name]['create']:
                    # Apps that have both ephemeral and persistent versions don't
                    # name their resources differently by default.
                    if 'ephemeral' in app_name:
                        obj['value'] = obj['value'] + '-ephemeral-' + str(ident)
                    elif 'persistent' in app_name:
                        obj['value'] = obj['value'] + '-persistent-' + str(ident)
                    else:
                        obj['value'] = obj['value'] + '-' + str(ident)

                if app_params and obj['name'] in app_params:
                    obj['value'] = app_params[obj['name']]

            ret = template
        return ret

    def create_a_processed_template(self, template):
        """
        A method that processes a raw template and returns it in dict format
        :param template: (required | dict) An raw/unprocessed template.
        :return: A processed template of type dict.
        """
        api_response = None
        try:
            api_response = self.ocp_processed_templates.create(body=template)
        except ApiException as e:
            logger.error("Exception when calling method create_a_processed_template : %s\n" % e)
        if api_response:
            return api_response.to_dict()
        else:
            return api_response

    def get_all_templates_in_a_namespace(self, project='openshift'):
        """
        A method that returns all availabel templates in a namespace
        :param project: (optional | str) the project/namespace that contains the templates.
        :return: An object of type V1TemplateList
        """
        api_response = None
        try:
            api_response = self.ocp_unprocessed_templates.get(namespace=project)
        except ApiException as e:
            logger.error("Exception when calling method get_all_templates_in_a_namespace: %s\n" % e)
        if api_response:
            return api_response
        else:
            return api_response

    def create_a_template_in_a_namespace(self, body, project='openshift'):
        """
        A method that adds a raw template to a namespace/project so it can
        be conveniently invoked by name for app deployment.
        :param body: (required | json/yaml) A raw template.
        :return: The template we added in dict format.
        """
        api_response = None
        try:
            api_response = self.ocp_unprocessed_templates.create(body, namespace=project)
        except ApiException as e:
            logger.error("Exception when calling method create_project_request: %s\n" % e)
        return api_response
