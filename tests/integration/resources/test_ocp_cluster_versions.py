import pytest
from unittest import mock

from piqe_ocp_lib.api.constants import CLUSTER_VERSION_OPERATOR_ID
from piqe_ocp_lib.api.resources.ocp_cluster_versions import OcpClusterVersion


@pytest.fixture(scope="session")
def ocp_cv(get_kubeconfig):
    kube_config_file = get_kubeconfig
    return OcpClusterVersion(kube_config_file=kube_config_file)


class TestOcpClusterVersion:

    def test_get_cluster_version(self, ocp_cv):
        """
        Verify that cluster version response is returned.
        :param ocp_cv: OcpClusterVersion class object
        :return:
        """
        expected_operator_name = "version"

        result = ocp_cv.get_cluster_version()

        assert result.metadata.name == expected_operator_name

    def test_get_cluster_id(self, ocp_cv):
        """
        Verify that cluster ID is returned
        :param ocp_cv: OcpClusterVersion class object
        :return:
        """
        cluster_version = ocp_cv.get_cluster_version()
        expected_cluster_id = cluster_version.spec.clusterID

        result = ocp_cv.get_cluster_id()

        assert isinstance(result, str)
        assert result == expected_cluster_id

    def test_build_spec_with_empty_input(self, ocp_cv):
        input_spec = {}
        cluster_version = ocp_cv.get_cluster_version()
        expected_output = {
            "apiVersion": ocp_cv.api_version,
            "kind": ocp_cv.kind,
            "spec": {"clusterId": cluster_version.spec.clusterID},
            "metadata": {
                "name": CLUSTER_VERSION_OPERATOR_ID,
                "resourceVersion": cluster_version.metadata.resourceVersion,
            }
        }

        result = ocp_cv._build_spec(input_spec)

        assert result == expected_output

    def test_build_spec_with_user_input(self, ocp_cv):
        input_spec = {
            "metadata": {"foo": "bar", "name": "fake"},
            "spec": {"quick": "fox", "clusterId": 1},
        }
        cluster_version = ocp_cv.get_cluster_version()
        expected_output = {
            "apiVersion": ocp_cv.api_version,
            "kind": ocp_cv.kind,
            "spec": {
                "clusterId": cluster_version.spec.clusterID,  # replaced
                "quick": "fox",  # merged
            },
            "metadata": {
                "name": CLUSTER_VERSION_OPERATOR_ID,  # replaced
                "resourceVersion": cluster_version.metadata.resourceVersion,
                "foo": "bar",  # merged
            }
        }

        result = ocp_cv._build_spec(input_spec)

        assert result == expected_output

    @pytest.mark.parametrize("available_updates,expected", [
        (None, []),
        ([
            {
                'channels': ['candidate-4.6', 'eus-4.6', 'fast-4.6', 'stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
            {
                'channels': ['candidate-4.6', 'eus-4.6', 'fast-4.6', 'stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.12'
            },
        ], ['4.6.8', '4.6.12']),
        ([
            {
                'channels': ['candidate-4.6', 'eus-4.6', 'fast-4.6', 'stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.12'
            },
            {
                'channels': ['candidate-4.6', 'eus-4.6', 'fast-4.6', 'stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
        ], ['4.6.12', '4.6.8']),
    ], ids=["no-updates", "sorted", "reverse-sorted"])
    def test_available_updates(self, ocp_cv, available_updates, expected):
        with mock.patch.object(ocp_cv, "get_cluster_version") as mock_version:
            mock_version.return_value.status.availableUpdates = available_updates

            result = ocp_cv.available_updates()

            mock_version.assert_called_once()

        assert isinstance(result, list)
        assert result == expected

    @pytest.mark.parametrize("available_updates,channel,expected", [
        ([
            {
                'channels': ['stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.12'
            },
            {
                'channels': ['stable-4.7'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
            {
                'channels': ['fast-4.7'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
        ], "stable-4.6", ["4.6.12"]),
        ([
            {
                'channels': ['fast-4.7'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
            {
                'channels': ['fast-4.7'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.12'
            },
        ], "fast-4.7", ["4.6.8", "4.6.12"]),
    ], ids=["filter-stable", "filter-fast"])
    def test_available_updates_with_filter(self, ocp_cv, available_updates, channel, expected):
        with mock.patch.object(ocp_cv, "get_cluster_version") as mock_version:
            mock_version.return_value.status.availableUpdates = available_updates

            result = ocp_cv.available_updates(channel=channel)

            mock_version.assert_called_once()

        assert isinstance(result, list)
        assert result == expected

    @pytest.mark.parametrize("available_channels,expected", [
        (None, set()),
        ([
            {
                'channels': ['candidate-4.6', 'eus-4.6', 'fast-4.6', 'stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
            {
                'channels': ['candidate-4.6', 'foo-4.7', 'fast-4.6', 'stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.9'
            },
        ], {'candidate-4.6', 'eus-4.6', 'fast-4.6', 'stable-4.6', 'foo-4.7'}),
    ], ids=["no-updates", "available-updates"])
    def test_available_channels(self, ocp_cv, available_channels, expected):
        with mock.patch.object(ocp_cv, "get_cluster_version") as mock_version:
            mock_version.return_value.status.availableUpdates = available_channels

            result = ocp_cv.available_channels()

            mock_version.assert_called_once()

        assert isinstance(result, set)
        assert result == expected

    @pytest.mark.parametrize("available_updates,channel,expected", [
        ([
            {
                'channels': ['stable-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.12'
            },
            {
                'channels': ['stable-4.7'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
        ], "foo", set()),
        ([
            {
                'channels': ['fast-4.7'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.8'
            },
            {
                'channels': ['fast-4.6'],
                'image': 'quay.io',
                'url': 'https://foo.bar',
                'version': '4.6.12'
            },
        ], "fast", {"fast-4.7", "fast-4.6"}),
    ], ids=["filter-nothing", "filter-fast"])
    def test_available_channels_with_filter(self, ocp_cv, available_updates, channel, expected):
        with mock.patch.object(ocp_cv, "get_cluster_version") as mock_version:
            mock_version.return_value.status.availableUpdates = available_updates

            result = ocp_cv.available_channels(kind=channel)

            mock_version.assert_called_once()

        assert isinstance(result, set)
        assert result == expected

    @pytest.mark.parametrize("available_updates,expected", [
        ([], None),
        (['4.6.8', '4.6.12'], '4.6.12'),
        (['4.6.12', '4.6.8'], '4.6.8'),  # Always last element in the list
    ], ids=["no-updates", "sorted", "reverse-sorted"])
    def test_latest_update_available(self, ocp_cv, available_updates, expected):
        with mock.patch.object(ocp_cv, "available_updates") as mock_version:
            mock_version.return_value = available_updates

            result = ocp_cv.latest_update_available()

            mock_version.assert_called_once()

        assert result == expected

    def test_update_channel(self, ocp_cv):
        input_channel = "fast-4.6"

        with mock.patch.object(ocp_cv, "_build_spec") as mock_build:
            expected_spec = {"spec": {"channel": input_channel}}
            mock_build.return_value = {"wrapped": expected_spec}

            with mock.patch.object(ocp_cv, "update_cluster_version") as mock_update:
                mock_update.return_value = "updated"

                result = ocp_cv.update_channel(input_channel)

                mock_build.assert_called_once_with(expected_spec)
                mock_update.assert_called_once_with({"wrapped": expected_spec})

        assert result == "updated"

    def test_upgrade_cluster_version_without_timeout(self, ocp_cv):
        version = "4.6.8"
        force = False

        with mock.patch.object(ocp_cv, "_build_spec") as mock_build:
            expected_build_spec = {
                "spec": {
                    "desiredUpdate": {
                        "force": force,
                        "version": version,
                    }
                }
            }
            mock_build.return_value = mock.sentinel.build_spec
            with mock.patch.object(ocp_cv, "update_cluster_version") as mock_update:
                mock_update.return_value = mock.sentinel.update_cluster

                result = ocp_cv.upgrade_cluster_version(version, force, timeout=0)

                mock_update.assert_called_once_with(mock.sentinel.build_spec)
                mock_build.assert_called_once_with(expected_build_spec)

        assert result == mock.sentinel.update_cluster
