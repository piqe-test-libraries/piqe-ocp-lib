import logging
from typing import Dict, List, Type, Union

from kubernetes.client import V1LimitRange, V1LimitRangeItem, V1LimitRangeSpec, V1ObjectMeta
from kubernetes.client.rest import ApiException
from openshift.dynamic.resource import ResourceInstance, ResourceList

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpLimitRanges(OcpBase):
    """
    OcpLimitRange Class extends OcpBase and encapsulates all methods
    related to openshift limit ranges.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super(OcpLimitRanges, self).__init__(kube_config_file=kube_config_file)
        self.api_version = "v1"
        self.kind = "LimitRange"
        self.ocp_limit_range = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_limit_ranges(self, namespace: str) -> ResourceList:
        """
        Get all LimitRanges from specific namespace
        :param namespace: (str) name of the namespace
        :return: LimitRanges response on Success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_limit_range.get(namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting LimitRanges : {e}\n")

        return api_response

    def get_limit_ranges_names(self, namespace: str) -> List[str]:
        """
        Get names of all LimitRanges from specific namespace
        :param namespace: (str) name of the namespace
        :return: List of LimitRanges names on Success OR Empty list on Failure
        """
        list_of_lr_names = list()
        lr_response = self.get_limit_ranges(namespace=namespace)

        if lr_response:
            for lr in lr_response.items:
                list_of_lr_names.append(lr.metadata.name)
        else:
            logger.warning(f"There are no LimitRanges in {namespace} namespace")

        return list_of_lr_names

    def delete_limit_ranges(self, namespace: str) -> ResourceInstance:
        """
        Delete the collection of LimitRange from specified namespace
        :param namespace: (str) name of namespace where LimitRange was created
        :return: Delete response on success OR None on Failure

        ResourceInstance[Status]:
          apiVersion: v1
          details:
            kind: limitrange
            name: test
            uid: aa1a8359-42b0-45f9-b44b-cd0ecbff6ef8
          kind: Status
          metadata: {}
          status: Success

        """
        api_response = None
        try:
            api_response = self.ocp_limit_range.delete(namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting LimitRanges: {e}\n")
        return api_response

    def create_a_limit_range(self, limit_ranges_body: Union[Dict, V1LimitRange]) -> ResourceInstance:
        """
        Create a LimitRanges in specific namespace
        :param limit_ranges_body (dict) LimitRanges definitions
        :return: CreateLimitRanges response on success OR None on Failure
        """
        create_lr_response = None
        try:
            create_lr_response = self.ocp_limit_range.create(body=limit_ranges_body)
        except ApiException as e:
            logger.exception(f"Exception while creating LimitRanges definitions : {e}\n")

        return create_lr_response

    def get_a_limit_range(self, name: str, namespace: str) -> ResourceInstance:
        """
        Get a specific LimitRanges from specific namespace
        :param name: (str) name of LimitRanges
        :param namespace: (str) namespace where LimitRanges is created
        :return: LimitRanges response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_limit_range.get(name=name, namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting a {name} LimitRanges : {e}\n")

        return api_response

    def delete_a_limit_range(self, name: str, namespace: str) -> ResourceInstance:
        """
        Delete a specified LimitRange from specified namespace
        :param name: (str) name of LimitRange
        :param namespace: (str) name of namespace where LimitRange was created
        :return: Delete response on success OR None on Failure

        ResourceInstance[Status]:
          apiVersion: v1
          details:
            kind: limitrange
            name: test
            uid: aa1a8359-42b0-45f9-b44b-cd0ecbff6ef8
          kind: Status
          metadata: {}
          status: Success

        """
        api_response = None
        try:
            api_response = self.ocp_limit_range.delete(name, namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting {name} LimitRanges: {e}\n")
        return api_response

    def update_a_limit_range(
        self, namespace: str, name: str, item_list: Union[List[Dict], List[V1LimitRangeItem]]
    ) -> ResourceInstance:
        """
        Method to change the limit ranges for a deployment.

        Note when patching a LimitRange make sure to include everything
        that you don't want changed either.
        :param namespace: The namespace containing the targeted
                          limit range
        :param name: The targeted limit range
        :param item_list: a list of V1LimitRangeItems or a list of LimitRangeItem dictionaries
        :return: A V1LimitRange object
        """
        spec = V1LimitRangeSpec(limits=item_list)
        body = {"spec": spec.to_dict()}
        api_response = None
        try:
            api_response = self.ocp_limit_range.patch(name=name, namespace=namespace, body=body)
        except ApiException as e:
            logger.error("Exception while updating LimitRange: %s\n", e)
        return api_response

    def replace_a_limit_range(self, limit_range_body: Union[Dict, V1LimitRange]) -> ResourceInstance:
        """
        Replace a LimitRanges in specific namespace
        :param limit_range_body (dict) LimitRanges definitions
        :return: CreateLimitRanges response on success OR None on Failure
        """
        replace_lr_response = None
        try:
            replace_lr_response = self.ocp_limit_range.replace(body=limit_range_body)
        except ApiException as e:
            logger.exception(f"Exception while replacing LimitRanges definitions : {e}\n")

        return replace_lr_response

    def container_limit_range_item(self) -> Union["OcpContainerLimit", V1LimitRangeItem]:
        """
        Build an OcpConatainterLimit object

        Example:
        item = ocp_lr.container_limit_range_item().memory(min="512Mb", max="1G").cpu(min="200M").build()

        :return: OcpContainerLimit object to build limit ranges
        """

        return OcpContainerLimit()

    def pod_limit_range_item(self) -> Union["OcpPodLimit", V1LimitRangeItem]:
        """
        Build an OcpPodLimit object

        Example:
        item = ocp_lr.pod_limit_range_item().memory(min="512Mb", max="1G").cpu(min="200M").build()

        :return: OcpPodLimit object to build limit ranges
        """

        return OcpPodLimit()

    def image_limit_range_item(self) -> Union["OcpImageLimit", V1LimitRangeItem]:
        """
        Build an OcpImageLimit object

        Example:
        item = ocp_lr.image_limit_range_item().memory(min="512Mb", max="1G").cpu(min="200M").build()

        :return: OcpImageLimit object to build limit ranges
        """

        return OcpImageLimit()

    def image_stream_limit_range_item(self) -> Union["OcpImageStreamLimit", V1LimitRangeItem]:
        """
        Build an OcpImageStreamLimit object

        Example:
        item = ocp_lr.image_stream_limit_range_item().images(max="20").image_tags(max="10").build()

        :return: OcpImageStreamLimit object to build limit ranges
        """

        return OcpImageStreamLimit()

    def persistent_volume_claim_limit_range_item(self) -> Union["OcpPersistentVolumeClaimLimit", V1LimitRangeItem]:
        """
        Build an OcpPersistentVolumeLimit object

        Example:
        item = ocp_lr.persistent_volume_claim_limit_range_item().storage(min="5G", max="20G").build()

        :return: OcpPersistentVolumeLimit object to build limit ranges
        """

        return OcpPersistentVolumeClaimLimit()

    def build_limit_range(self, name: str, namespace: str, item_list: List[V1LimitRangeItem]) -> V1LimitRange:
        """
        Build an V1LimitRange Object using the list of OcpLimitRangeItems
        :return:  V1LimitRange Object
        """

        if not isinstance(item_list, list):
            raise Exception("You must provide a list of V1LimitRangeItems")
        items = [item.to_dict() for item in item_list]
        lrs = V1LimitRangeSpec(limits=items)
        return V1LimitRange(
            api_version="v1", kind="LimitRange", metadata=V1ObjectMeta(name=name, namespace=namespace), spec=lrs
        )


class OcpLimitRangeItem(object):
    """
    OcpContainerLimit Class is a builder that encapsulates
    that kubernetes V1LimitRangeItem class so that it's easier to build with values
    related to limit ranges.
    :param type: (str) The V1LimitRangeItem type to set
    :return: None
    """

    def __init__(self, type):

        self._model = V1LimitRangeItem(type=type)

    def type(self) -> str:
        """
        This returns the type of V1LimitRangeItem builder.
        :return: V1LimitRangeItem type
        """

        return self._model.type

    def _set_properties(
        self,
        type: str,
        min: Union[str, None] = None,
        max: Union[str, None] = None,
        default: Union[str, None] = None,
        default_request: Union[str, None] = None,
        max_limit_ratio: Union[str, None] = None,
    ):
        """
        Set the properties on the V1LimitRangeItem
        :param type: (str) the resource type to limit (cpu, memory, storage, etc.)
        :param min: (str) the minimum value to set for the resource type an OpenShift resource can request
        :param max: (str) the maximum value to set for the resource type an Openshift resource can request
        :param default: (str) the default value to set for the resource type an Openshift can use if not specified
        :param default_request: (str) the default value to set for the resource type an Openshift can request if
        not specified
        :param max_limit_ratio: (str)The maximum limit-to-request ratio for an OpenShift resource
        :return: None
        """

        if min:
            if self._model.min is None:
                self._model.min = {type: min}
            else:
                self._model.min.update({type: min})
        if max:
            if self._model.max is None:
                self._model.max = {type: max}
            else:
                self._model.max.update({type: max})
        if default:
            if self._model.default is None:
                self._model.default = {type: default}
            else:
                self._model.default.update({type: default})
        if default_request:
            if self._model.default_request is None:
                self._model.default_request = {type: default_request}
            else:
                self._model.default_request.update({type: default_request})
        if max_limit_ratio:
            if self._model.max_limit_request_ratio is None:
                self._model.max_limit_request_ratio = {type: max_limit_ratio}
            else:
                self._model.max_limit_request_ratio.update({type: max_limit_ratio})

    def build(self) -> V1LimitRangeItem:
        """
        This returns the final product that a client can use to create LimitRanges.
        :return: V1LimitRangeItem object
        """

        lri = self._model
        self._model = V1LimitRangeItem(type=lri.type)
        return lri


class OcpContainerLimit(OcpLimitRangeItem):
    """
    OcpContainerLimit Class extends OcpLimitRangeItem and encapsulates the specific
    methods to set Container related limit ranges.
    :return: None
    """

    def __init__(self):

        super(OcpContainerLimit, self).__init__(type="Container")

    def cpu(
        self,
        min: Union[str, None] = None,
        max: Union[str, None] = None,
        default: Union[str, None] = None,
        default_request: Union[str, None] = None,
        max_limit_ratio: Union[str, None] = None,
    ) -> Type["OcpContainerLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type Container
        :param min: (str) the minimum value to set for CPU a Container resource can request
        :param max: (str) the maximum value to set for CPU a Container resource can request
        :param default: (str) the default value to set for CPU a Container can use if not specified
        :param default_request: (str) the default value to set for CPU a Container can request if
        not specified
        :param max_limit_ratio: (str)The maximum limit-to-request ratio for a Container
        :return: OcpContainerLimit object
        """
        self._set_properties(
            type="cpu",
            min=min,
            max=max,
            default=default,
            default_request=default_request,
            max_limit_ratio=max_limit_ratio,
        )
        return self

    def memory(
        self,
        min: Union[str, None] = None,
        max: Union[str, None] = None,
        default: Union[str, None] = None,
        default_request: Union[str, None] = None,
        max_limit_ratio: Union[str, None] = None,
    ) -> Type["OcpContainerLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type Container
        :param min: (str) the minimum value to set for Memory a Container resource can request
        :param max: (str) the maximum value to set for Memory a Container resource can request
        :param default: (str) the default value to set for Memory a Container can use if not specified
        :param default_request: (str) the default value to set for Memory a Container can request if
        not specified
        :param max_limit_ratio: (str)The maximum limit-to-request ratio for a Container
        :return: OcpContainerLimit object
        """
        self._set_properties(
            type="memory",
            min=min,
            max=max,
            default=default,
            default_request=default_request,
            max_limit_ratio=max_limit_ratio,
        )
        return self


class OcpPodLimit(OcpLimitRangeItem):
    """
    OcpPodLimit Class extends OcpLimitRangeItem and encapsulates the specific
    methods to set Pod related limit ranges.
    :return: None
    """

    def __init__(self):

        super(OcpPodLimit, self).__init__(type="Pod")

    def cpu(
        self, min: Union[str, None] = None, max: Union[str, None] = None, max_limit_ratio: Union[str, None] = None
    ) -> Type["OcpPodLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type Pod
        :param min: (str) the minimum value to set for CPU a Pod resource can request across all containers
        :param max: (str) the maximum value to set for CPU a Pod resource can request across all containers
        :param max_limit_ratio: (str)The maximum limit-to-request ratio for a Container in a Pod
        :return: OcpContainerLimit object
        """

        self._set_properties(type="cpu", min=min, max=max, max_limit_ratio=max_limit_ratio)
        return self

    def memory(
        self, min: Union[str, None] = None, max: Union[str, None] = None, max_limit_ratio: Union[str, None] = None
    ) -> Type["OcpPodLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type Pod
        :param min: (str) the minimum value to set for Memory a Pod resource can request across all containers
        :param max: (str) the maximum value to set for Memory a Pod resource can request across all containers
        :param max_limit_ratio: (str)The maximum limit-to-request ratio for a Container in a Pod
        :return: OcpContainerLimit object
        """

        self._set_properties(type="memory", min=min, max=max, max_limit_ratio=max_limit_ratio)
        return self


class OcpImageLimit(OcpLimitRangeItem):
    """
    OcpImageLimit Class extends OcpLimitRangeItem and encapsulates the specific
    methods to set Image related limit ranges.
    :return: None
    """

    def __init__(self):

        super(OcpImageLimit, self).__init__(type="openshift.io/Image")

    def storage(self, max: Union[str, None] = None) -> Type["OcpImageLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type Image
        :param max: (str) the maximum value to set for Storage an Image can be pushed to a registry
        :return: OcpContainerLimit object
        """

        self._set_properties(type="storage", max=max)
        return self


class OcpImageStreamLimit(OcpLimitRangeItem):
    """
    OcpImageStreamLimit Class extends OcpLimitRangeItem and encapsulates the specific
    methods to set ImageStream related limit ranges.
    :return: None
    """

    def __init__(self):

        super(OcpImageStreamLimit, self).__init__(type="openshift.io/ImageStream")

    def image_tags(self, max: Union[str, None] = None) -> Type["OcpImageStreamLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type ImageStream
        :param max: (str) the maximum value of unique image tags in the imagestream.spec.tags parameter in
        imagestream spec.
        :return: OcpContainerLimit object
        """

        self._set_properties(type="openshift.io/image-tags", max=max)
        return self

    def images(self, max: Union[str, None] = None) -> Type["OcpImageStreamLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type ImageStream
        :param max: (str) the maximum value of unique image references in the imagestream.status.tags parameter in
        the imagestream spec.
        :return: OcpContainerLimit object
        """

        self._set_properties(type="openshift.io/images", max=max)
        return self


class OcpPersistentVolumeClaimLimit(OcpLimitRangeItem):
    """
    OcpPesistentVolumeClaimLimit Class extends OcpLimitRangeItem and encapsulates the specific
    methods to set PersistentVolumeClaim related limit ranges.
    :return: None
    """

    def __init__(self):

        super(OcpPersistentVolumeClaimLimit, self).__init__(type="PersistentVolumeClaim")

    def storage(
        self, min: Union[str, None] = None, max: Union[str, None] = None
    ) -> Type["OcpPersistentVolumeClaimLimit"]:
        """
        Set the properties on the V1LimitRangeItem of type PersistentVolumeClaim
        :param min: (str) the minimum value to set for Storage that can be requested in a volume claim
        :param max: (str) the maximum value to set for Storage that can be requested in a volume claim
        :return: OcpContainerLimit object
        """
        self._set_properties(type="storage", min=min, max=max)
        return self
