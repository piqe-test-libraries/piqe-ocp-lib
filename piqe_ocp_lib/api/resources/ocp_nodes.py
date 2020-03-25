from .ocp_base import OcpBase
from kubernetes.client.rest import ApiException
import logging
import subprocess
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpNodes(OcpBase):
    """
    OcpNodes Class extends OcpBase and encapsulates all methods
    related to managing Openshift nodes.
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
        self.api_version = 'v1'
        self.kind = 'Node'
        self.ocp_nodes = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_all_nodes(self, label_selector=None):
        """
        Method that returns a list of node objects
        :param label_selector: Used to return a a list of nodes based on the provided label(s)
        :return: V1NodeList on success. None on failure.
        """
        node_object_list = None
        try:
            node_object_list = self.ocp_nodes.get(label_selector=label_selector)
        except ApiException as e:
            logger.error("Exception when calling method list_node: %s\n", e)
        return node_object_list

    def get_all_node_names(self):
        """
        Method that returns a list of all node names based on node objects
        :return: List of unfiltered node names on success. None on failure.
        """
        node_names = []
        try:
            node_object_list = self.get_all_nodes(label_selector=None)
            for node in node_object_list.items:
                node_names.append(node.metadata.name)
        except ApiException as e:
            logger.error("Exception encountered while gathering node names: %s\n", e)
        return node_names

    def get_a_node(self, node_name):
        """
        Method returns a node object by name

        :param node_name: The name of the node.
        :return: V1Node on success. None on failure.
        """
        node_object = None
        try:
            node_object = self.ocp_nodes.get(name=node_name)
        except ApiException as e:
            logger.error("Exception encountered while getting a node by name: %s\n", e)
        return node_object

    def watch_all_nodes(self):
        # We need to determine if a use case for this exists.
        pass

    def watch_a_node(self, node_name):
        pass

    def create_a_node(self, node_name):
        pass

    def delete_a_node(self, node_name):
        pass

    def label_a_node(self, node_name, labels):
        """
        Method that patches a node as a means to apply a label to it.
        :param node_name: The name of the node to patch
        :param labels: A dictionary containing the key,val labels
        :return: A V1DeploymentConfig object
        """
        body = {'metadata': {'labels': labels}}
        api_response = None
        try:
            api_response = self.ocp_nodes.patch(name=node_name, body=body)
        except ApiException as e:
            logger.error("Exception while patching nodes: %s\n", e)
        return api_response

    def get_node_status(self, node_name):
        """
        Return the status of a node based on the condition type Ready.
        :param node_name:
        :return: The status for the condition. Either True or False
        """
        node_object = None
        try:
            node_object = self.ocp_nodes.get(name=node_name)
            for condition in node_object.status.conditions:
                condition_type = condition.get('type')
                if condition_type == 'Ready':
                    return condition.get('status')
        except ApiException as e:
            logger.error("Exception encountered while determining the node condition: %s\n", e)
        return node_object

    def get_node_roles(self, node_name):
        """
        Return the roles assigned to the nodes by looking for the following:
        node-role.kubernetes.io/master: ''
        node-role.kubernetes.io/worker: ''
        :param node_name: The node to examine
        :return: List containing the awssigned roles. Currently Master and/or Worker.
        """
        node_role = []
        try:
            node_object = self.ocp_nodes.get(name=node_name)
            # labels are returned as tuples
            for label in node_object.metadata.labels:
                if label[0] == 'node-role.kubernetes.io/master':
                    node_role.append('Master')
                if label[0] == 'node-role.kubernetes.io/worker':
                    node_role.append('Worker')
        except ApiException as e:
            logger.error("Exception encountered while getting a node by name: %s\n", e)
        return node_role

    def execute_command_on_a_node(self, node_name, command_to_execute):
        """
        Executes the provided command on the specified node_name.
        :param node_name:  The name of the node on which command gets executed
        :param command_to_execute:
        :return:  return code, stdout, stderr of the command executed
        """
        # Pod Name
        pod_name = "execute-on-%s" % node_name

        # Check if pod exists
        command = "kubectl get pods | grep %s" % pod_name
        logger.info("Executing command: %s", command)
        subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = subp.communicate()
        ret = subp.returncode
        logger.info("Command - %s - execution status:\n"
                    "RETCODE: %s\nSTDOUT: %s\nSTDERR: %s\n",
                    command, ret, out, err)
        if ret != 0:
            # Spin a new container for the node
            container_definition = """
{
  "spec": {
    "hostPID": true,
    "hostNetwork": true,
    "nodeSelector": { "kubernetes.io/hostname": "%s" },
    "tolerations": [{
      "operator": "Exists"
    }],
    "containers": [
      {
        "name": "nsenter",
        "image": "alexeiled/nsenter:2.34",
        "command": [
          "/nsenter", "--all", "--target=1", "--", "su", "-"
        ],
        "stdin": true,
        "tty": true,
        "securityContext": {
          "privileged": true
        },
        "resources": {
          "requests": {
            "cpu": "10m"
          }
        }
      }
    ]
  }
}""" % node_name
            command = ("kubectl run %s --restart=Never --image "
                       "overriden --overrides '%s'" % (pod_name, container_definition))
            logger.info("Executing command : %s", command)
            subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out, err = subp.communicate()
            ret = subp.returncode
            logger.info("Command - %s - execution status:\n"
                        "RETCODE: %s\nSTDOUT: %s\nSTDERR: %s\n",
                        command, ret, out, err)
            if ret != 0:
                return ret, out, err
        # Execute the command
        command = "kubectl exec %s %s" % (pod_name, command_to_execute)
        logger.info("Executing command: %s", command)
        subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = subp.communicate()
        ret = subp.returncode
        logger.info("Command - %s - execution status:\n"
                    "RETCODE: %s\nSTDOUT: %s\nSTDERR: %s\n",
                    command, ret, out, err)
        return ret, out, err
