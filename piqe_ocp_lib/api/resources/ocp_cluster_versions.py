from typing import Dict, List, Set, Union
from datetime import datetime, timedelta
import logging
import time

from piqe_ocp_lib.api.resources.ocp_base import OcpBase
from piqe_ocp_lib.api.constants import CLUSTER_VERSION_OPERATOR_ID, CLUSTER_POLLING_SECONDS_INTERVAL
from kubernetes.client.rest import ApiException
from piqe_ocp_lib import __loggername__

logger = logging.getLogger(__loggername__)


class OcpClusterVersion(OcpBase):
    """
    OcpClusterVersion class extends OcpBase and encapsulates all methods
    related to managing Openshift Cluster Version.
    :param kube_config_file: A kubernetes config file.
    :return: None
    """

    def __init__(self, kube_config_file=None):
        super().__init__(kube_config_file=kube_config_file)
        self.api_version = 'config.openshift.io/v1'
        self.kind = 'ClusterVersion'
        self.ocp_cv = self.dyn_client.resources.get(api_version=self.api_version, kind=self.kind)

    def get_cluster_version(self):
        """
        Get ClusterVersion operator details
        :return: ClusterVersion detail API response on success OR None on Failure
        """
        cluster_version_response = None
        try:
            cluster_version_response = self.ocp_cv.get(name=CLUSTER_VERSION_OPERATOR_ID)
        except ApiException as e:
            logger.error("Exception while getting cluster version %s : %s\n", e)

        return cluster_version_response

    def update_cluster_version(self, cv_body):
        """
        Update ClusterVersion operator
        :param cv_body: (dict) Updated body of ClusterVersion operator
        :return: (Dict) ClusterVersion API response on success OR None on Failure
        """
        if not isinstance(cv_body, dict):
            logger.error("Cluster version body is empty. Please provide config body with field to be updated")
            return

        # Add/Update resourceVersion under metadata and clusterID under spec to match of existing resource.These two
        # field are also required to properly update ClusterVersion operator. Without these two fields,API call will
        # succeed but changes won't be applied.
        cluster_version = self.get_cluster_version()

        cv_body["metadata"]["resourceVersion"] = cluster_version["metadata"]["resourceVersion"]
        cv_body["spec"]["clusterID"] = cluster_version["spec"]["clusterID"]

        try:
            return self.ocp_cv.replace(body=cv_body)
        except ApiException as e:
            logger.exception("Exception while updating cluster version : %s\n" % e)

    def get_cluster_id(self) -> str:
        """
        Get cluster ID
        :return: cluster_id on success or None on failure
        """
        cluster_version_response = self.get_cluster_version()
        return cluster_version_response.spec.clusterID

    def _build_spec(self, cv_body: Dict) -> Dict:
        """
        Add required fields in the user's input body.
        :return: Updated dict with required values
        """
        cluster_version = self.get_cluster_version()

        if not cluster_version:
            return cv_body

        cv_body.update({"apiVersion": self.api_version, "kind": self.kind})
        metadata = {
            "name": CLUSTER_VERSION_OPERATOR_ID,
            "resourceVersion": cluster_version.metadata.resourceVersion,  # Required for successfull API call
        }
        spec = {"clusterId": cluster_version.spec.clusterID}  # Required for successfull API call

        cv_body["metadata"] = {**cv_body.get("metadata", {}), **metadata}
        cv_body["spec"] = {**cv_body.get("spec", {}), **spec}
        return cv_body

    def available_updates(self, channel: str = None) -> List[str]:
        """
        Get available versions to update
        :return: list of available versions
        """
        cluster_version = self.get_cluster_version()
        available_updates = cluster_version.status.availableUpdates

        if not isinstance(available_updates, list):
            # API returns null instead of empty list
            logger.debug("No update available.")
            return []

        if channel:
            available_updates = filter(lambda x: channel in x["channels"], available_updates)

        available_updates = [update["version"] for update in available_updates]

        return available_updates

    def available_channels(self, kind: str = None) -> Set[str]:
        """
        Get available channels to upgrade
        :return: set of available channels
        """
        cluster_version = self.get_cluster_version()
        available_channels = cluster_version.status.availableUpdates

        if not isinstance(available_channels, list):
            # API returns null instead of empty list
            logger.debug("No update available.")
            return set()

        if kind:
            available_channels = filter(
                lambda updates: any(kind in channel for channel in updates["channels"]),
                available_channels
            )

        available_channels = set().union(*[e["channels"] for e in available_channels])

        return available_channels

    def latest_update_available(self, channel: str = None) -> Union[str, None]:
        """
        Get latest version available to upgrade
        :return: String with latest value OR None
        """
        cluster_available_updates = self.available_updates(channel=channel)

        try:
            return cluster_available_updates[::-1][0]  # Sorted by OpenShift's API
        except IndexError:
            logger.debug("Cluster already at latest version.")

    def update_channel(self, channel: str):
        """
        Change update channel
        :param channel: (str) name of the channel
        :return: (ClusterVersion) object
        """
        cv_body = {"spec": {"channel": channel}}
        cv_body = self._build_spec(cv_body)
        return self.update_cluster_version(cv_body)

    def upgrade_cluster_version(self, version: str, force: bool = False, timeout: int = 0) -> Dict:
        """
        Upgrade cluster to desired version
        :param force: whether to force the update or not
        :param timeout: minutes to wait for upgrade completion
        :return: ClusterVersion API response
        """
        from piqe_ocp_lib.api.resources.ocp_health_checker import OcpHealthChecker

        def wait_until_upgraded(timeout: int):
            """
            Polling of CVO status until upgrade is completed or fail otherwise
            :return: CVO object OR None
            """
            ends_at = datetime.now() + timedelta(minutes=timeout)
            health_checker = OcpHealthChecker()

            while datetime.now() < ends_at:
                cluster_version = self.get_cluster_version()

                if health_checker.check_cluster_version_operator_health():
                    logger.info("Cluster upgraded successfully.")
                    return cluster_version
                else:
                    sorting_key = lambda x: datetime.strptime(x.lastTransitionTime, "%Y-%m-%dT%H:%M:%SZ")
                    latest_status = sorted(cluster_version.status.conditions, key=sorting_key, reverse=True)[0]
                    logger.info(f"Upgrade in progress, checking again in {CLUSTER_POLLING_SECONDS_INTERVAL} seconds.")
                    logger.info(f"The latest event is {latest_status.type} - {getattr(latest_status, 'message', '')}")
                    time.sleep(CLUSTER_POLLING_SECONDS_INTERVAL)
            else:
                # Polling exhausted
                logger.error(f"Failed to verify cluster upgrade during {timeout} minutes.")

        cv_body = self._build_spec({
            "spec": {
                "desiredUpdate": {
                    "force": force,
                    "version": version,
                }
            }
        })

        ocp_cv_upgrade_response = self.update_cluster_version(cv_body)

        return wait_until_upgraded(timeout) if timeout else ocp_cv_upgrade_response
