import logging

from kubernetes.client.rest import ApiException

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)

"""
Both openshift Pipeline and PipelineRun object requires openshift-pipeline operator to be install.
It is not installed natively. Please use OLM or our operator automation.
"""


class OcpPipelines(OcpBase):
    """
    OcpPipelines Class extends OcpBase and encapsulates all methods
    related to Openshift Pipelines.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super(OcpPipelines, self).__init__(kube_config_file=kube_config_file)
        self.api_version = "tekton.dev/v1beta1"
        self.kind = "Pipeline"
        self.ocp_pipeline = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_pipelline(self, body):
        """
        Create a Pipeline in specific namespace
        :param body (dict) Pipeline definitions
        :return: PipelineRuns response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_pipeline.create(body=body)
        except ApiException as e:
            logger.exception(f"Exception while creating openshift Pipeline definitions : {e}\n")

        return api_response

    def get_pipelines(self, namespace):
        """
        Get all Pipelines from specific namespace
        :param namespace: (str) name of the namespace
        :return: Pipelines response on Success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_pipeline.get(namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting openshift pipelines : {e}\n")

        return api_response

    def get_a_pipeline(self, name, namespace):
        """
        Get a specific pipeline from specific namespace
        :param name: (str) name of pipeline
        :param namespace: (str) namespace where pipeline was created
        :return: Pipeline response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_pipeline.get(name=name, namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting a {name} Pipeline : {e}\n")

        return api_response

    def get_pipeline_names(self, namespace):
        """
        Get names of all Pipelines from specific namespace
        :param namespace: (str) name of the namespace
        :return: List of Pipeline names on Success OR Empty list on Failure
        """
        pipeline_names = list()
        pipeline_response = self.get_pipelines(namespace=namespace)

        if pipeline_response:
            for pipeline_run in pipeline_response.items:
                pipeline_names.append(pipeline_run.metadata.name)
        else:
            logger.warning(f"There are no Pipelines in {namespace} namespace")

        return pipeline_names

    def delete_pipeline(self, name, namespace):
        """
        Delete a specified Pipeline from specified namespace
        :param name: (str) name of Pipeline
        :param namespace: (str) name of namespace where Pipeline was created
        :return: Delete response on success OR None on Failure

        ResourceInstance[Status]:
          apiVersion: v1
          details:
            group: tekton.dev
            kind: pipelines
            name: seed-iot-frontend-yp3sbp
            uid: 683586d8-94c0-48a0-80b2-0639a0e2102d
          kind: Status
          metadata: {}
          status: Success

        """
        api_response = None
        try:
            api_response = self.ocp_pipeline.delete(name, namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting {name} Pipeline: {e}\n")
        return api_response


class OcpPipelineRuns(OcpBase):
    """
    OcpPipelineRuns Class extends OcpBase and encapsulates all methods
    related to Openshift PipelineRuns.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super(OcpPipelineRuns, self).__init__(kube_config_file=kube_config_file)
        self.api_version = "tekton.dev/v1beta1"
        self.kind = "PipelineRun"
        self.ocp_pipeline_runs = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def create_pipeline_run(self, body):
        """
        Create a PipelineRuns in specific namespace
        :param body (dict) PipelineRuns definitions
        :return: PipelineRuns response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_pipeline_runs.create(body=body)
        except ApiException as e:
            logger.exception(f"Exception while creating PipelineRuns definitions : {e}\n")

        return api_response

    def get_pipeline_runs(self, namespace):
        """
        Get all PipelineRuns from specific namespace
        :param namespace: (str) name of the namespace
        :return: PipelineRuns response on Success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_pipeline_runs.get(namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting pipeline runs : {e}\n")

        return api_response

    def get_a_pipeline_run(self, name, namespace):
        """
        Get a specific pipeline run from specific namespace
        :param name: (str) name of PipelineRun
        :param namespace: (str) namespace where pipeline runs was created
        :return: PipelineRuns response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_pipeline_runs.get(name=name, namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting a {name} PipelineRuns : {e}\n")

        return api_response

    def get_pipeline_run_names(self, namespace):
        """
        Get names of all PipelineRuns from specific namespace
        :param namespace: (str) name of the namespace
        :return: List of PipelineRuns names on Success OR Empty list on Failure
        """
        pipeline_runs_names = list()
        pr_response = self.get_pipeline_runs(namespace=namespace)

        if pr_response:
            for pipeline_run in pr_response.items:
                pipeline_runs_names.append(pipeline_run.metadata.name)
        else:
            logger.warning(f"There are no PipelineRuns in {namespace} namespace")

        return pipeline_runs_names

    def delete_pipeline_run(self, name, namespace):
        """
        Delete a specified PipelineRun from specified namespace
        :param name: (str) name of PipelineRuns
        :param namespace: (str) name of namespace where PIpelineRuns was created
        :return: Delete response on success OR None on Failure

        ResourceInstance[Status]:
          apiVersion: v1
          details:
            group: tekton.dev
            kind: pipelineruns
            name: seed-iot-frontend-yp3sbp
            uid: 683586d8-94c0-48a0-80b2-0639a0e2102d
          kind: Status
          metadata: {}
          status: Success

        """
        api_response = None
        try:
            api_response = self.ocp_pipeline_runs.delete(name, namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting {name} PipelineRun: {e}\n")
        return api_response

    def is_pipeline_run_succeeded(self, namespace, pipeline_run_name, timeout):
        """
        Method that watches a pipeline runs in a specific namespace
        :param timeout: timeout in sec
        :param namespace: The namespace where the targeted pod resides
        :param pipeline_run_name: The name of the pipeline run to watch
        :return: boolean
        """
        logger.info(f"Watching pod {pipeline_run_name} for readiness")
        pipeline_run_ready = False
        field_selector = "metadata.name={}".format(pipeline_run_name)
        for event in self.ocp_pipeline_runs.watch(namespace=namespace, field_selector=field_selector, timeout=timeout):
            for pipeline_run_condition in event["object"]["status"]["conditions"]:
                if pipeline_run_condition["status"] == "True" and pipeline_run_condition["type"] == "Succeeded":
                    logger.info("Pipeline Run %s is in %s state", pipeline_run_name, pipeline_run_condition["status"])
                    pipeline_run_ready = True
                    return pipeline_run_ready
        logger.error(
            "Pipeline Run %s is in %s state. Message : %s",
            pipeline_run_name,
            pipeline_run_condition["status"],
            pipeline_run_condition["message"],
        )
        return pipeline_run_ready
