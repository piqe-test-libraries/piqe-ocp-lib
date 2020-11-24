#!/usr/bin/python

""" OCP Cluster Config schemas """

import yaml
import logging
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class ocp_app(object):
    """
        ocp_app class defines application's template, number of replicas and
        app_count of a ocp cluster
    """
    # ocp_app_config_types defines the type of each attribute of the class
    ocp_app_config_types = {
        'app_template': str,
        'app_count': int,
        'app_replicas': int,
        'app_labels': dict,
        'app_params': dict
    }

    def __init__(self, app):
        """
        app defined by app_template, number of app_replicas, app_count

        :param app: dict containing information about the ocp_app
        """
        self._app_template = None
        self._app_count = None
        self._app_replicas = None
        self._app_labels = None
        self._app_params = None

        if app is not None:
            # app template
            self._app_template = app.get('app_template')
            if not isinstance(
                    self._app_template,
                    self.ocp_app_config_types.get('app_template')):
                raise ValueError(
                    "'app_template': (Expected '%s', Actual '%s')" % (
                        self.ocp_app_config_types['app_template'],
                        self._app_template
                    )
                )

            # app count
            self._app_count = app.get('app_count')
            if not isinstance(
                    self._app_count,
                    self.ocp_app_config_types.get('app_count')):
                raise ValueError(
                    "'app_count': (Expected '%s', Actual '%s')" % (
                        self.ocp_app_config_types['app_count'],
                        self._app_count
                    )
                )

            # app replicas
            self._app_replicas = app.get('app_replicas')
            if not isinstance(
                    self._app_replicas,
                    self.ocp_app_config_types.get('app_replicas')):
                raise ValueError(
                    "'app_replicas': (Expected '%s', Actual '%s')" % (
                        self.ocp_app_config_types['app_replicas'],
                        self._app_replicas
                    )
                )

            # app labels
            self._app_labels = app.get('app_labels')
            if not isinstance(
                    self._app_labels,
                    self.ocp_app_config_types.get('app_labels')):
                raise ValueError(
                    "'app_labels': (Expected '%s', Actual '%s')" % (
                        self.ocp_app_config_types['app_labels'],
                        self._app_labels
                    )
                )
            """
                No strict check required for app_param since this is an optional value
            """
            # app params
            if app.get('app_params'):
                self._app_params = app.get('app_params')
                if not isinstance(self._app_params, self.ocp_app_config_types.get('app_params')):
                    logging.error("app_params are attribute is not of type dict.")
            else:
                app['app_params'] = None
            # if not isinstance(
            #         self._app_params,
            #         self.ocp_app_config_types.get('app_params')):
            #     raise ValueError(
            #         "'app_params': (Expected '%s', Actual '%s')" % (
            #             self.ocp_app_config_types['app_params'],
            #             self._app_params
            #         )
            #     )

    @property
    def app_template(self):
        """ Gets the app_template name of this ocp_app.

        :return: app_template name of this ocp_app.
        :type: str
        """
        return self._app_template

    @app_template.setter
    def app_template(self, app_template):
        """Sets the app_template  of this ocp_app.

        :param api_template: The app_template  of this ocp_app.
        :type: str
        """
        self._app_template = app_template

    @property
    def app_count(self):
        """ Gets the app_count of this ocp_app

        :return: app_count of this ocp_app
        :type: int
        """
        return self._app_count

    @app_count.setter
    def app_count(self, app_count):
        """ Sets the app_count of this ocp_app.

        :param api_count: The app_count of this ocp_app.
        :type: int
        """
        self._app_count = app_count

    @property
    def app_replicas(self):
        """ Gets the app_replica count of this ocp_app

        :return: app_replica count of this ocp_app
        :type: int
        """
        return self._app_replicas

    @app_replicas.setter
    def app_replicas(self, app_replicas):
        """ Sets the app_replicas of this ocp_app.

        :param api_: The app_replicas  of this ocp_app.
        :type: int
        """
        self._app_replicas = app_replicas

    @property
    def app_labels(self):
        """ Gets the app_labels of this ocp_app

        :return: app_labels of this ocp_app
        :type: dict
        """
        return self._app_labels

    @app_labels.setter
    def app_labels(self, app_labels):
        """ Sets the app_labels of this ocp_app.

        :param api_: The app_labels  of this ocp_app.
        :type: dict
        """
        self._app_labels = app_labels

    @property
    def app_params(self):
        """ Gets the app_params of this ocp_app

        :return: app_params of this ocp_app
        :type: dict
        """
        return self._app_params

    @app_params.setter
    def app_params(self, app_params):
        """ Sets the app_params of this ocp_app.

        :param api_: The app_params  of this ocp_app.
        :type: dict
        """
        self._app_params = app_params


class ocp_project(object):
    """ ocp_project defines project in the ocp cluster i.e project_name
    and list of all apps of the project/namespace in ocp cluster.
    Each app in the projects list is of type 'ocp_app'
    """
    ocp_project_config_types = {
        'project_name': str,
        'apps': list,
        'project_labels': dict
    }

    def __init__(self, project=None):
        """ Project as defined by project_name and list of apps

        :param project: dict containing project_name, list of apps
        """
        self._project_name = None
        self._apps = None
        self._project_labels = None

        if project is not None:
            # project name
            self._project_name = project.get('project_name')
            if not isinstance(
                    self._project_name,
                    self.ocp_project_config_types.get('project_name')):
                raise ValueError(
                    "'project_name': (Expected '%s', Actual '%s')" % (
                        self.ocp_project_config_types['project_name'],
                        type(self._project_name)
                    )
                )

            # apps
            apps = project.get('apps')
            if not isinstance(
                    apps, self.ocp_project_config_types.get('apps')):
                raise ValueError(
                    "'apps': (Expected '%s', Actual '%s')" % (
                        self.ocp_project_config_types['apps'],
                        type(apps)
                    )
                )
            else:
                self._apps = []
                for app in apps:
                    try:
                        app_obj = ocp_app(app)
                        self._apps.append(app_obj)
                    except ValueError as _e:
                        raise ValueError(_e)

            # project labels
            self._project_labels = project.get('project_labels')
            if not isinstance(
                    self._project_labels,
                    self.ocp_project_config_types.get('project_labels')):
                raise ValueError(
                    "'project_labels': (Expected '%s', Actual '%s')" % (
                        self.ocp_project_config_types['project_labels'],
                        type(self._project_labels)
                    )
                )

    @property
    def project_name(self):
        """ Gets project_name of this ocp_project

        :return: project_name of this ocp_project
        :type: str
        """
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        """ Sets the project_name of this ocp_project

        :param project_name: Name of the ocp_project
        :type: str
        """
        self._project_name = project_name

    @property
    def apps(self):
        """ Gets list of apps of this ocp_project

        :return: list of apps objects of this ocp_project
        :type: list
        """
        return self._apps

    @apps.setter
    def apps(self, apps):
        """ Sets app or list of apps of type ocp_app of this ocp_project

        :param apps: app or list of apps of type ocp_app of this ocp_project
        :type: list of ocp_app class object
        """
        if self._apps is not None:
            if isinstance(apps, ocp_app):
                self._apps.append(ocp_app)
            elif isinstance(apps, list):
                self._apps.extend(apps)
        else:
            if isinstance(apps, ocp_app):
                self._apps = [ocp_app]
            elif isinstance(apps, list):
                self._apps = ocp_app

    @property
    def project_labels(self):
        """ Gets project_name of this ocp_project

        :return: project_name of this ocp_project
        :type: str
        """
        return self._project_labels

    @project_labels.setter
    def project_labels(self, project_labels):
        """ Sets the project_name of this ocp_project

        :param project_name: Name of the ocp_project
        :type: str
        """
        self._project_labels = project_labels


class ocp_cluster_metadata(object):
    """Class containing ocp cluster metadata
    """
    ocp_cluster_metadata_types = {
        'ocp_version': str,
        'cns_required': bool,
        'cns_version': str,
        'cns_nodes': int,
        'routers': list,
        'heketi': str,
    }

    def __init__(self, metadata):
        """ ocp cluster metadata. i.e ocp_version, cns_version,
        number of cns_nodes, routers, heketi info.

        :param metadata:  dict of ocp cluster metadata
        """
        self._ocp_version = None
        self._cns_required = None
        self._cns_version = None
        self._cns_nodes = None
        self._routers = None
        self._heketi = None

        # ocp_version
        self._ocp_version = (
            metadata.get('prerequisites', {}).get('ocp_version'))
        if not isinstance(
                self._ocp_version,
                self.ocp_cluster_metadata_types.get('ocp_version')):
            raise ValueError(
                "'ocp_version': (Expected '%s', Actual '%s)" % (
                    self.ocp_cluster_metadata_types['ocp_version'],
                    type(self._ocp_version)
                )
            )

        # cns required
        self._cns_required = (
            metadata.get('prerequisites', {}).get('cns', {}).get('required'))
        if not isinstance(
                self._cns_required,
                self.ocp_cluster_metadata_types.get('cns_required')):
            raise ValueError(
                "'cns_required': (Expected '%s', Actual '%s)" % (
                    self.ocp_cluster_metadata_types['cns_required'],
                    type(self._cns_required)
                )
            )

        # cns_version
        self._cns_version = (
            metadata.get('prerequisites', {}).get('cns', {}).get('version'))
        if not isinstance(
                self._cns_version,
                self.ocp_cluster_metadata_types.get('cns_version')):
            raise ValueError(
                "'cns_version': (Expected '%s', Actual '%s)" % (
                    self.ocp_cluster_metadata_types['cns_version'],
                    type(self._cns_version)
                )
            )

        # cns nodes
        self._cns_nodes = (
            metadata.get('prerequisites', {}).get('cns', {}).get('cns_nodes'))
        if not isinstance(
                self._cns_nodes,
                self.ocp_cluster_metadata_types.get('cns_nodes')):
            raise ValueError(
                "'cns_nodes': (Expected '%s', Actual '%s)" % (
                    self.ocp_cluster_metadata_types['cns_nodes'],
                    type(self._cns_nodes)
                )
            )

        # routers
        self._routers = (
            metadata.get('prerequisites', {}).get('routers'))
        if not isinstance(
                self._routers,
                self.ocp_cluster_metadata_types.get('routers')):
            if isinstance(self._routers, str):
                self._routers = [self._routers]
            else:
                raise ValueError(
                    "'routers': (Expected '%s', Actual '%s)" % (
                        self.ocp_cluster_metadata_types['routers'],
                        type(self._routers)
                    )
                )

        # heketi
        self._heketi = (
            metadata.get('prerequisites', {}).get('heketi'))
        if not isinstance(
                self._heketi,
                self.ocp_cluster_metadata_types.get('heketi')):
            raise ValueError(
                "'heketi': (Expected '%s', Actual '%s)" % (
                    self.ocp_cluster_metadata_types['heketi'],
                    type(self._heketi)
                )
            )

    @property
    def ocp_version(self):
        """ Gets ocp_version of this ocp_cluster

        :return: ocp_version of this ocp_cluster
        :type: str
        """
        return self._ocp_version

    @ocp_version.setter
    def ocp_version(self, ocp_version):
        """ Sets ocp_version of this ocp_cluster

        :param ocp_version: ocp_version of this ocp_cluster
        :type: str
        """
        self._ocp_version = ocp_version

    @property
    def cns_required(self):
        """ Gets if cns_required in this ocp_cluster

        :return: is cns_required in this ocp_cluster
        :type: bool
        """
        return self._cns_required

    @cns_required.setter
    def cns_required(self, cns_required):
        """ Sets cns_required if cns is required in this ocp_cluster

        :param cns_required: if cns is required in this ocp_cluster
        :type: bool
        """
        self._cns_required = cns_required

    @property
    def cns_version(self):
        """ Gets cns_version of this ocp_cluster

        :return: cns_version of this ocp_cluster
        :type: str
        """
        return self._cns_version

    @cns_version.setter
    def cns_version(self, cns_version):
        """ Sets cns_version of this ocp_cluster

        :param cns_version: cns_version of this ocp_cluster
        :type: str
        """
        self._cns_version = cns_version

    @property
    def cns_nodes(self):
        """ Gets number of cns_nodes in this ocp_cluster

        :return: number of cns_nodes in this ocp_cluster
        :type: int
        """
        return self._cns_nodes

    @cns_nodes.setter
    def cns_nodes(self, cns_nodes):
        """ Sets number of cns_nodes in this ocp_cluster

        :param cns_nodes: number of cns_nodes in this ocp_cluster
        :type: int
        """
        self._cns_nodes = cns_nodes

    @property
    def routers(self):
        """ Gets routers of this ocp_cluster

        :return: routers of this ocp_cluster
        :type: list
        """
        return self._routers

    @routers.setter
    def routers(self, routers):
        """ Sets routers of this ocp_cluster

        :param routers: list of routers of this ocp_cluster
        :type: list
        """
        if self._routers is not None:
            if isinstance(routers, str):
                self._routers.append(routers)
            elif isinstance(routers, list):
                self._routers.extend(routers)
        else:
            if isinstance(routers, str):
                self._routers = [routers]
            elif isinstance(routers, list):
                self._routers = routers

    @property
    def heketi(self):
        """ Gets heketi name of this cluster

        :return: heketi name of this cluster
        :type: str
        """
        return self._heketi

    @heketi.setter
    def heketi(self, heketi):
        """ Sets heketi name of this ocp_cluster

        :param heketi: heketi name of this ocp_cluster
        :type: str
        """
        self._heketi = heketi


class populate_ocp_cluster_config(object):
    """
      ocp_populate_cluster_config (dict): The key is attribute name
        and the value is attribute type.
    """
    nodes = []
    populate_ocp_cluster_config_types = {
        'metadata': ocp_cluster_metadata,
        'projects': list
    }

    def __init__(self, populate_ocp_cluster_config_file):
        """ config to create the ocp_cluster as defined in the Populate
        cluster YAML config file

        :param populate_ocp_cluster_config_file: YAML config file to
        populate ocp cluster
        """
        self._metadata = None
        self._projects = None

        # Load the YAML config file to a dictionary
        cluster_config = None
        try:
            with open(populate_ocp_cluster_config_file) as _fd:
                try:
                    cluster_config = yaml.load(_fd, Loader=yaml.FullLoader)
                except Exception as yamlerror:
                    raise yaml.YAMLError("YAML Error:\n %s" % yamlerror)
        except Exception as ioerror:
            raise IOError(ioerror)

        if cluster_config is None:
            raise ValueError("Invalid cluster config dict")

        # get metadata
        cluster_metadata = cluster_config.get('metadata')
        if not isinstance(cluster_metadata, dict):
            raise ValueError(
                "'metadata': (Expected '%s', Actual '%s')" %
                (str(dict), type(cluster_metadata))
            )
        else:
            try:
                self._metadata = ocp_cluster_metadata(
                    cluster_metadata)
            except ValueError as _e:
                raise ValueError(_e)

        # get list of projects
        projects = cluster_config.get('projects', {})
        if not isinstance(
                projects,
                self.populate_ocp_cluster_config_types.get('projects')):
            raise ValueError(
                "'projects': (Expected '%s', Actual '%s')" % (
                    self.populate_ocp_cluster_config_types['projects'],
                    type(projects)
                )
            )
        else:
            self._projects = []
            for project in projects:
                try:
                    ocp_project_obj = ocp_project(project)
                    self._projects.append(ocp_project_obj)
                except ValueError as _e:
                    raise ValueError(_e)

    @property
    def metadata(self):
        """ Gets ocp_cluster metadata

        :return: ocp_cluster metadata
        ;type: ocp_cluster_metadata obj
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metada6a):
        """ Sets ocp_cluster metadata

        :param metada6a: ocp_cluster_metadata object
        :type: ocp_cluster_metadata
        """
        self._metadata = metada6a

    @property
    def projects(self):
        """ Gets list of projects in this ocp_cluster

        :return: list of ocp_project objs
        :type: list[ocp_project]
        """
        return self._projects

    @projects.setter
    def projects(self, projects):
        """ Sets projects of this ocp_cluster

        :param projects: list of ocp_project objs
        :type:  list[ocp_project]
        """
        if self._projects is not None:
            if isinstance(projects, ocp_project):
                self._projects.append(projects)

            elif isinstance(projects, list):
                self._projects.extend(projects)
        else:
            if isinstance(projects, ocp_project):
                self._projects = [projects]
            elif isinstance(projects, list):
                self._projects = projects
