from enum import Enum, auto
import logging
from typing import Any, Dict, List, Optional, Type, Union

from kubernetes.client import (
    V1ObjectMeta,
    V1ResourceQuota,
    V1ResourceQuotaSpec,
    V1ResourceQuotaStatus,
    V1ScopedResourceSelectorRequirement,
    V1ScopeSelector,
)
from kubernetes.client.rest import ApiException
from openshift.dynamic.resource import ResourceInstance, ResourceList

from piqe_ocp_lib import __loggername__
from piqe_ocp_lib.api.resources.ocp_base import OcpBase

logger = logging.getLogger(__loggername__)


class OcpResourceQuota(OcpBase):
    """
    OcpResourceQuota Class extends OcpBase and encapsulates all methods
    related to openshift resource quotas.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = "v1"
        self.kind = "ResourceQuota"
        self.ocp_resource_quota = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_resource_quotas(self, namespace: str) -> ResourceList:
        """
        Get all ResourceQuotas from specific namespace
        :param namespace: (str) name of the namespace
        :return: ResourceQuotas response on Success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_resource_quota.get(namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting ResourceQuotas : '{e}'\n")

        return api_response

    def get_resource_quotas_names(self, namespace: str) -> List[str]:
        """
        Get names of all ResourceQuotas from specific namespace
        :param namespace: (str) name of the namespace
        :return: List of ResourceQuotas names on Success OR Empty list on Failure
        """
        list_of_rq_names = list()
        rq_response = self.get_resource_quotas(namespace=namespace)

        if rq_response:
            for rq in rq_response.items:
                list_of_rq_names.append(rq.metadata.name)
        else:
            logger.warning(f"There are no ResourceQuotas in '{namespace}' namespace")

        return list_of_rq_names

    def delete_resource_quotas(self, namespace: str) -> ResourceInstance:
        """
        Delete the collection of ResourceQuota from specified namespace
        :param namespace: (str) name of namespace where ResourceQuota was created
        :return: Delete response on success OR None on Failure

        ResourceInstance[Status]:
          apiVersion: v1
          details:
            kind: ResourceQuota
            name: test
            uid: aa1a8359-42b0-45f9-b44b-cd0ecbff6ef8
          kind: Status
          metadata: {}
          status: Success

        """
        api_response = None
        try:
            api_response = self.ocp_resource_quota.delete(namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting ResourceQuotas: '{e}'\n")
        return api_response

    def create_a_resource_quota(self, resource_quota_body: Union[Dict, V1ResourceQuota]) -> ResourceInstance:
        """
        Create a ResourceQuota in specific namespace
        :param resource_quota_body (dict) ResourceQuotas definitions
        :return: CreateResourceQuotas response on success OR None on Failure
        """
        create_lr_response = None
        try:
            create_lr_response = self.ocp_resource_quota.create(body=resource_quota_body)
        except ApiException as e:
            logger.exception(f"Exception while creating ResourceQuotas definitions : '{e}'\n")

        return create_lr_response

    def get_a_resource_quota(self, name: str, namespace: str) -> ResourceInstance:
        """
        Get a specific ResourceQuota from specific namespace
        :param name: (str) name of ResourceQuotas
        :param namespace: (str) namespace where ResourceQuotas is created
        :return: ResourceQuotas response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_resource_quota.get(name=name, namespace=namespace)
        except ApiException as e:
            logger.error(f"Exception while getting a {name} ResourceQuota : '{e}'\n")

        return api_response

    def delete_a_resource_quota(self, name: str, namespace: str) -> ResourceInstance:
        """
        Delete a specified ResourceQuota from specified namespace
        :param name: (str) name of ResourceQuota
        :param namespace: (str) name of namespace where ResourceQuota was created
        :return: Delete response on success OR None on Failure
        """
        api_response = None
        try:
            api_response = self.ocp_resource_quota.delete(name, namespace)
        except ApiException as e:
            logger.exception(f"Exception while deleting {name} ResourceQuota: {e}\n")
        return api_response

    def update_a_resource_quota(
        self, namespace: str, name: str, spec: Union[Dict, V1ResourceQuotaSpec]
    ) -> ResourceInstance:
        """
        Method to change the resource quota for a project.

        Note when patching a ResourceQuota make sure to include everything
        that you don't want changed either.
        :param namespace: The namespace containing the targeted
                          resource quota
        :param name: The targeted resource quota
        :param spec: a V1ResourceQuotaSpec or a ResourceQuotaSpec dictionary
        :return: A ResourceInstace object
        """

        """
       Can't update/patch a quota with different scope values once a quota has been 
       created with scopes values. It always throws a 422 error from OpenShift.
       If you really want to patch a quota so that it does not have scopes define. 
       You're better off running the delete_a_resource_quota and
       create_a_resource_quota using the new scope values
       """

        if isinstance(spec, dict):
            spec = V1ResourceQuotaSpec(**spec)

        body = {"spec": spec.to_dict()}
        api_response = None
        try:
            api_response = self.ocp_resource_quota.patch(name=name, namespace=namespace, body=body)
        except ApiException as e:
            logger.error("Exception while updating ResourceQuota: %s\n", e)
        return api_response

    def replace_a_resource_quota(self, resource_quota_body: Union[Dict, V1ResourceQuota]) -> ResourceInstance:
        """
        Replace a ResourceQuota in specific namespace
        :param resource_quota_body (dict) ResourceQuota definitions
        :return: ResourceInstance response on success OR None on Failure
        """

        """
        Can't replace a quota with different scope values once a quota has been 
        created with scopes values. It always throws a 422 error from OpenShift.
        If you really want to replace a quota so that it does not have scopes define. 
        You're better off running the delete_a_resource_quota and
        create_a_resource_quota using the new scope values
        """
        replace_rq_response = None
        try:
            replace_rq_response = self.ocp_resource_quota.replace(body=resource_quota_body)
        except ApiException as e:
            logger.exception(f"Exception while replacing ResourceQuota definitions : {e}\n")

        return replace_rq_response

    def get_a_resource_quota_status(self, name: str, namespace: str) -> V1ResourceQuotaStatus:
        """
        Query a ResourceQuota in specific namespace for status usage
        :param name: (str) name of ResourceQuota
        :param namespace: (str) namespace where ResourceQuota is created
        :return: V1ResourceQuotaStatus object
        """

        """
        The dynamic client builds subresource APIs for resources as well.
        In this case ResourceQuota has a Subresource called Status that represents
        the ResourceQuotaStatus API to see usage statistics.
        "kind": "ResourceQuota",
        "name": "resourcequotas/status"
        """
        resp = self.ocp_resource_quota.status.get(name=name, namespace=namespace)
        status = resp.status
        return V1ResourceQuotaStatus(**status)

    def resource_scope_selector_expression(
        self,
    ) -> Union["OcpScopeSelectorExpression", V1ScopedResourceSelectorRequirement]:
        """
        Create a OcpScopeSelectorExpression object that is used to build a V1ScopedResourceSelectorRequirement.
        For more info about scopeSelectors refer to
        https://kubernetes.io/docs/concepts/policy/resource-quotas/#resource-quota-per-priorityclass

        #Example:
        item = ocp_rq.resource_scope_selector_expression().priority_class_scope()._in().values(vals=['high']).build()

        :return: OcpScopeSelectorExpression object
        """

        return OcpScopeSelectorExpression()

    def resource_quota_spec(self) -> Union["OcpResourceQuotaSpec", V1ResourceQuotaSpec]:
        """
        Create an OcpResourceQuotaSpec object that is used to build a V1ResourceQuotaSpec

        #Example 1:
        item = ocp_rq.resource_quota_spec().memory(requests='512Mi').cpu(requests='1200M').terminating_scope().build()

        #Example 2:
        item = ocp_rq.resource_quota_spec().ephemeral_storage(requests="1G").storage_class(class_name='gold',
                                                                                           requests='8G').build()

        :return: OcpPodLimit object to build resource quotas
        """

        return OcpResourceQuotaSpec()

    def resource_quota(self, name: str, namespace: str, spec: V1ResourceQuotaSpec) -> V1ResourceQuota:
        """
        Build an V1ResourceQuota Object using the V1ResourceQuotaSpec
        :return:  V1ResourceQuota Object
        """

        return V1ResourceQuota(
            api_version="v1", kind="ResourceQuota", metadata=V1ObjectMeta(name=name, namespace=namespace), spec=spec
        )


class CamelCaseEnum(Enum):
    """
    CamelCaseEnum Class is an Enum that overrides the default value generator function so that
    we can reduce the redundancy of defining the Enum key and then explicitly defining the
    value a string representation of the key. Example below

    TERMINATING = "Terminating"
    NOT_TERMINATING = "NotTerminating"
    """

    def _generate_next_value_(name, start, count, last_values):
        normal_name = ""
        tup = name.split("_")
        for item in tup:
            normal_name += item.lower().capitalize()

        return normal_name


class Scopes(CamelCaseEnum):
    """
    Scopes Class is an Enum that provides the default scopes a resource
    quota can be assigned to measure against. These scopes can be assigned
    by the scopes key in a ResourceQuota or by way of a ScopeSelector using
    the scopeName key.
    """

    TERMINATING = auto()
    NOT_TERMINATING = auto()
    BEST_EFFORT = auto()
    NOT_BEST_EFFORT = auto()
    PRIORITY_CLASS = auto()


class Operators(CamelCaseEnum):
    """
    Operators Class is an Enum that provides the default operators a ScopeSelector
    can use to match the ResourceQuota.
    """

    IN = auto()
    NOT_IN = auto()
    EXISTS = auto()
    DOES_NOT_EXISTS = auto()


class OcpScopeSelectorExpression:
    """
    OcpScopeSelectorExpression Class is a builder that encapsulates
    that kubernetes V1ScopedResourceSelectorRequirement class so that it's
    easier to build the ScopeSelector with the required values.
    :param ocp_spec_obj: (obj) a OcpResourceQuotaSpec object
    :return: None
    """

    def __init__(self, ocp_spec_obj=None):

        self._ocp_spec = ocp_spec_obj

        """
        I have to save them as attributes because the
        V1ScopedResourceSelectorRequirement class throws exceptions
        if I initialize it without the scope_name and operator parameter.
        This is the first kubernetes model object I've encountered that 
        doesn't like initializing with no parameters.
        """
        self._scope_name = None
        self._operator = None
        self._values = None

    def terminating_scope(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the scope_name to 'Terminating' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._scope_name = Scopes.TERMINATING.value
        return self

    def not_terminating_scope(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the scope_name to 'NotTerminating' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._scope_name = Scopes.NOT_TERMINATING.value
        return self

    def not_best_effort_scope(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the scope_name to 'NotBestEffort' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._scope_name = Scopes.NOT_BEST_EFFORT.value
        return self

    def best_effort_scope(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the scope_name to 'BestEffort' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._scope_name = Scopes.BEST_EFFORT.value
        return self

    def priority_class_scope(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the scope_name to 'PriorityClass' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._scope_name = Scopes.PRIORITY_CLASS.value
        return self

    def in_(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the operator to 'In' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._operator = Operators.IN.value
        return self

    def not_in(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the operator to 'NotIn' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._operator = Operators.NOT_IN.value
        return self

    def exists(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the operator to 'Exists' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._operator = Operators.EXISTS.value
        return self

    def not_exists(self) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the operator to 'DoesNotExists' on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._operator = Operators.DOES_NOT_EXISTS.value
        return self

    def values(self, vals: List[str]) -> Type["OcpScopeSelectorExpression"]:
        """
        Set the values to 'the list of string on the V1ScopedResourceSelectorRequirement
        :return: OcpScopeSelectorExpression object
        """

        self._values = vals
        return self

    def _is_operator_in_or_notin_val_set_rule(self) -> bool:
        """
        a rule to check that if the operator is to In or NotIn that there needs
        to be a value assigned to the V1ScopedResourceSelectorRequirement

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: bool
        """

        if self._operator in [Operators.IN.value, Operators.NOT_IN.value] and self._values is None:
            raise Exception("The operator %s requires at least one value to be set!" % self._operator)
        return True

    def _is_operator_exists_or_notexists_val_not_set_rule(self) -> bool:
        """
        a rule to check that if the operator is to Exists or DoesNotExists that there
        needs NOT to be a value assigned to the V1ScopedResourceSelectorRequirement

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: bool
        """

        if self._operator in [Operators.EXISTS.value, Operators.DOES_NOT_EXISTS.value] and self._values is not None:
            raise Exception(
                "A value should not be set for the expression when the operator %s or %s is set!"
                % (Operators.EXISTS.value, Operators.DOES_NOT_EXISTS.value)
            )
        return True

    def _is_operator_exists_set_for_req_scopes_rule(self) -> bool:
        """
        a rule to check that if the scope is set to one of the below scopes that the
        operator needs to be set to Exists in the V1ScopedResourceSelectorRequirement

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: bool
        """

        if (
            self._scope_name
            in [
                Scopes.TERMINATING.value,
                Scopes.NOT_TERMINATING.value,
                Scopes.BEST_EFFORT.value,
                Scopes.NOT_BEST_EFFORT.value,
            ]
            and self._operator != Operators.EXISTS.value
        ):
            raise Exception(
                "The scope %s in the expression requires operator to be %s!"
                % (self._scope_name, Operators.EXISTS.value)
            )
        return True

    def done(self) -> Type["OcpResourceQuotaSpec"]:
        """
        Builds a V1ScopedResourceSelectorRequirement and assigns it to the
        V1Selector object assigned to the OcpResourceQuotaSpec. This should
        only be used when building the SelectorScope expression
        as part of the OcpResourceQuotaSpec building in a nested fashion.

        #Example

        ocp_rq.resource_quota_spec().scope_selector().priority_class_scope().in_().values(vals=['high']).done().build()

        :return: OcpResourceQuotaSpec object
        """
        selector = self.build()
        if self._ocp_spec:
            if self._ocp_spec._model.scope_selector.match_expressions:
                self._ocp_spec._model.scope_selector.match_expressions.append(selector)
            else:
                self._ocp_spec._model.scope_selector.match_expressions = [selector]
            return self._ocp_spec

    def build(self) -> V1ScopedResourceSelectorRequirement:
        """
        Builds a V1ScopedResourceSelectorRequirement

        #Example

        ocp_rq.resource_scope_selector_expression().priority_class_scope().in_().values(vals=['high']).build()

        :return: OcpResourceQuotaSpec object
        """

        # Let's run our rule check first before we return the final product
        # that way we catch them upfront vs when making the the API call
        self._is_operator_exists_or_notexists_val_not_set_rule()
        self._is_operator_exists_set_for_req_scopes_rule()
        self._is_operator_in_or_notin_val_set_rule()

        selector = V1ScopedResourceSelectorRequirement(scope_name=self._scope_name, operator=self._operator)
        if self._values:
            selector.values = self._values

        # reset the values
        self._values = None
        self._operator = None
        self._scope_name = None

        return selector


class OcpResourceQuotaSpec:
    """
    OcpContainerLimit Class is a builder that encapsulates
    that kubernetes V1ResourceQuotaSpec class so that it's easier to build with values
    related to resource quotas.
    :param type: (str) The V1ResourceQuotaSpec type to set
    :return: None
    """

    def __init__(self):

        self._model = V1ResourceQuotaSpec()

    def _set_hard(self, type: str = "hard", **kwargs: str):
        """
        Set the the hard property on the V1ResourceQuotaSpec
        :param type: (str) the property - hard
        :param kwargs: (str) a dictionary of key/values that get set. keys are the resource names (cpu, memory, etc.)
        :return: None
        """
        props = {k.replace("_", "."): v for k, v in kwargs.items() if v is not None}

        self._set_properties(type=type, properties=props)

    def _set_scopes(self, scopes: List, type: str = "scopes"):
        """
        Set the the scopes property on the V1ResourceQuotaSpec
        :param type: (str) the property - scopes
        :param kwargs: (list) a list of strings that refer to the scopes
        :return: None
        """

        self._set_properties(type=type, properties=scopes)

    def _set_scope_selectors(self, selector: V1ScopedResourceSelectorRequirement):
        """
        Set the the scopes_selector expression into the V1ScopeSelector in the
        V1ResourceQuotaSpec
        :param selector: (str) the property - scopes
        :param kwargs: (list) a list of strings that refer to the scopes
        :return: None
        """

        if self._model.scope_selector.match_expressions:
            self._model.scope_selector.match_expressions.append(selector)
        else:
            self._model.scope_selector.match_expressions = [selector]

    def _set_properties(self, type: str, properties: Any):
        """
        Set the properties on the V1ResourceQuotaSpec
        :param type: (str) the property type (hard/scopes)
        :param properties: (any) either a list or dict to set for the property
        :return: None
        """

        if hasattr(self._model, type):
            if getattr(self._model, type) is None:
                setattr(self._model, type, properties)
            else:
                if isinstance(properties, dict):
                    getattr(self._model, type).update(properties)
                if isinstance(properties, list):
                    getattr(self._model, type).extend(properties)

    def scope_selector(
        self, selector: Optional[V1ScopedResourceSelectorRequirement] = None
    ) -> Union[Type["OcpScopeSelectorExpression"], Type["OcpResourceQuotaSpec"]]:
        """
        Set the scope_selector on the V1ResourceQuotaSpec if provided. If not,
        instantiate the OcpScopeSelectorExpression builder to build as part of the chain
        :param type: (str) the property type (hard/scopes)
        :param properties: (any) either a list or dict to set for the property
        :return: None
        """

        if self._model.scope_selector is None:
            selector_obj = V1ScopeSelector()
            self._model.scope_selector = selector_obj

        if selector:
            print("selector: %s" % selector)
            self._set_scope_selectors(selector)
            return self

        return OcpScopeSelectorExpression(ocp_spec_obj=self)

    def resource(
        self, resource: str, requests: Optional[str] = None, count: Optional[str] = None
    ) -> Type["OcpResourceQuotaSpec"]:
        """
        Use this to either set requests quota on an extended resources or
        a standard resource that doesn't have a generic object count implementation

        #Example extended resource request

        ocp_rq.resource_quota_spec().resource(resource="nvidia.com/gpu", requests="4")

        #Example standard resource count with no generic object count

        ocp_rq.resource_quota_spec().resource(resource="deployments.apps", count="4")

        :param resource: (str) the name of the extended/standard resource
        :param requests: (str) the number of requests to limit for the extended resource in a project
        :param count: (str) the number of objects to limit for the extended/standard resource in a project
        :return: OcpResourceQuotaSpec object
        """

        params = {}
        if requests:
            params["requests_%s" % resource] = requests
        if count:
            params["count/%s" % resource] = count

        self._set_hard(**params)
        return self

    def cpu(self, limits: Optional[str] = None, requests: Optional[str] = None) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on cpu resources on the V1ResourceQuotaSpec
        :param limits: (str) Across all pods in a non-terminal state, the sum of CPU limits cannot exceed
        :param requests: (str) Across all pods in a non-terminal state, the sum of CPU requests cannot exceed
        :return: OcpResourceQuotaSpec object
        """
        self._set_hard(limits_cpu=limits, requests_cpu=requests)
        return self

    def memory(self, limits: Optional[str] = None, requests: Optional[str] = None) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on memory resources on the V1ResourceQuotaSpec
        :param limits: (str) Across all pods in a non-terminal state, the sum of memory limits cannot exceed
        :param requests: (str) Across all pods in a non-terminal state, the sum of memory requests cannot exceed
        :return: OcpResourceQuotaSpec object
        """
        self._set_hard(limits_memory=limits, requests_memory=requests)
        return self

    def storage(self, requests: str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on storage resources on the V1ResourceQuotaSpec
        :param requests: (str) The sum of storage requests across all persistent volume claims in any state cannot
        exceed this value.
        :return: OcpResourceQuotaSpec object
        """
        self._set_hard(requests_storage=requests)
        return self

    def ephemeral_storage(
        self, limits: Union[str, None] = None, requests: Union[str, None] = None
    ) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on ephemeral-storage resources on the V1ResourceQuotaSpec
        :param limits: (str) Across all pods in a non-terminal state, the sum of ephemeral-storage limits cannot exceed
        :param requests: (str) Across all pods in a non-terminal state, the sum of ephemeral-storage requests cannot
        exceed
        :return: OcpResourceQuotaSpec object
        """
        params = {}
        if limits:
            params["limits_ephemeral-storage"] = limits
        if requests:
            params["requests_ephemeral-storage"] = requests

        self._set_hard(**params)
        return self

    def storage_class(
        self, class_name: str, requests: Optional[str] = None, persistent_volume_claims: Optional[str] = None
    ) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on storage-class resources on the V1ResourceQuotaSpec
        :param class_name: (str) Name of the storage class, i.e. gold, low-priority, etc.
        :param requests: (str) Across all persistent volume claims in a project, the sum of storage requested in the
        storage class cannot exceed this value
        :param persistent_volume_claims: (str) Across all persistent volume claims in a project,
        the total number of claims in the storage class cannot exceed this value.
        exceed
        :return: OcpResourceQuotaSpec object
        """

        params = {}
        full_name = "%s_storageclass.storage.k8s.io/" % class_name
        storage_key = full_name + "requests_storage"
        pvc_key = full_name + "persistentvolumeclaims"
        if requests:
            params[storage_key] = requests
        if persistent_volume_claims:
            params[pvc_key] = persistent_volume_claims

        self._set_hard(**params)
        return self

    def terminating_scope(self) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the scopes to Terminating the V1ResourceQuotaSpec

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: OcpResourceQuotaSpec object
        """
        scope = [Scopes.TERMINATING.value]
        self._set_scopes(scopes=scope)
        return self

    def not_terminating_scope(self) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the scopes to NotTerminating the V1ResourceQuotaSpec

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: OcpResourceQuotaSpec object
        """
        scope = [Scopes.NOT_TERMINATING.value]
        self._set_scopes(scopes=scope)
        return self

    def not_best_effort_scope(self) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the scopes to NotBestEffort the V1ResourceQuotaSpec

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: OcpResourceQuotaSpec object
        """

        scope = [Scopes.NOT_BEST_EFFORT.value]
        self._set_scopes(scopes=scope)
        return self

    def best_effort_scope(self) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the scopes to BestEffort the V1ResourceQuotaSpec

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: OcpResourceQuotaSpec object
        """

        scope = [Scopes.BEST_EFFORT.value]
        self._set_scopes(scopes=scope)
        return self

    def priority_class_scope(self) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the scopes to PriorityClass the V1ResourceQuotaSpec

        https://kubernetes.io/docs/concepts/policy/resource-quotas/#quota-scopes
        :return: OcpResourceQuotaSpec object
        """

        scope = [Scopes.PRIORITY_CLASS.value]
        self._set_scopes(scopes=scope)
        return self

    def persistent_volume_claims(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on persistent volume claim objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of persistent volume claims (PVCs) that can exist in the project.
        :return: OcpResourceQuotaSpec object
        """

        name = self.persistent_volume_claims.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def pods(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on pod objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of pods in a non-terminal state that can exist in the project.
        :return: OcpResourceQuotaSpec object
        """

        name = self.pods.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def replication_controllers(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on replicationcontroller objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of replication controllers that can exist in the project.
        :return: OcpResourceQuotaSpec object
        """

        name = self.replication_controllers.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def services(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on service objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of services that can exist in the project
        :return: OcpResourceQuotaSpec object
        """

        name = self.services.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def services_loadbalancers(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on service objects of type loadbalancer on the V1ResourceQuotaSpec
        :param count: (str) The total number of services of type LoadBalancer that can exist in the project.
        :return: OcpResourceQuotaSpec object
        """

        name = self.services_loadbalancers.__name__.replace("_", ".")
        params = {name: count}
        self._set_hard(**params)
        return self

    def service_nodeports(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on service objects of type nodeport on the V1ResourceQuotaSpec
        :param count: (str) The total number of services of type NodePort that can exist in the project.
        :return: OcpResourceQuotaSpec object
        """

        name = self.service_nodeports.__name__.replace("_", ".")
        params = {name: count}
        self._set_hard(**params)
        return self

    def secrets(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on secret objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of secrets that can exist in the project
        :return: OcpResourceQuotaSpec object
        """

        name = self.secrets.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def config_maps(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on config map objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of ConfigMap objects that can exist in the project
        :return: OcpResourceQuotaSpec object
        """

        name = self.config_maps.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def resource_quotas(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on resourcequota objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of ResourceQuotas that can exist in the namespace.
        :return: OcpResourceQuotaSpec object
        """

        name = self.resource_quotas.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def image_streams(self, count=str) -> Type["OcpResourceQuotaSpec"]:
        """
        Set the hard limits on imagestream objects on the V1ResourceQuotaSpec
        :param count: (str) The total number of image streams that can exist in the project.
        :return: OcpResourceQuotaSpec object
        """

        name = "openshift.io/" + self.image_streams.__name__.replace("_", "")
        params = {name: count}
        self._set_hard(**params)
        return self

    def build(self) -> V1ResourceQuota:
        """
        This returns the final product that a client can use to create ResourceQuota.
        :return: V1ResourceQuotaSpec object
        """

        lri = self._model
        self._model = V1ResourceQuotaSpec()
        return lri
