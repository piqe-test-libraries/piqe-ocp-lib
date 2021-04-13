"""
Setting pytest config files to be used by test fixtures defined under the test directory
"""
import os
from datetime import datetime
import pytest
from piqe_ocp_lib.piqe_api_logger import piqe_api_logger
from glusto.core import Glusto as g
from piqe_ocp_lib import __loggername__


def pytest_addoption(parser):
    parser.addoption(
        "--openshift-version",
        action="store",
        default="latest",
        help="Version of OpenShift to test against for functional tests",
    )
    parser.addoption("--openshift-first-master", action="store", help="Openshift first master HOSTNAME/IP")
    parser.addoption("--openshift-default-tests-config", action="store", help="Openshift default tests config file")
    parser.addoption("--openshift-tests-log-dir", action="store", default="./logs/", help="Openshift tests logs dir")
    parser.addoption("--openshift-tests-log-level", action="store", default="INFO", help="Openshift tests log level")
    parser.addoption("--log-to-stdout", action="store", default="True", help="Log output to stdout as well as file")
    parser.addoption(
        "--filter",
        action="append",
        type=str,
        default=[],
        help="A filter to select which projects to deploy. This option"
        "takes a single or comma separated list of labels.",
    )
    parser.addoption(
        "--span", action="store", type=int, default=60, help="The duration for running the longevity in seconds"
    )
    parser.addoption(
        "--replicas",
        action="store",
        type=int,
        default=5,
        help="The max number of replicas to scale apps in the longevity test",
    )
    parser.addoption(
        "--kubeconfig", action="store", default=None, help="The full path to the kubeconfig file to be used"
    )
    parser.addoption(
        "--kubeconfig-3x",
        action="store",
        default=None,
        help="The full path to the kubeconfig file to be used for ocp3x cluster",
    )
    parser.addoption(
        "--cluster-config",
        action="store",
        default=None,
        help="The config yaml file describing the desired cluster layout",
    )
    parser.addoption("--num-jenkins-jobs", action="store", default=None, help="The number of jenkins job to create")
    parser.addoption(
        "--num-locust-clients",
        action="store",
        default=None,
        help="Number of concurrent Locust users. Only used together with --no-web",
    )
    parser.addoption(
        "--locust-hatch-rate",
        action="store",
        default=None,
        help="The rate per second in which clients are spawned. Only used together with --no-web",
    )


def pytest_report_header(config):
    return "OpenShift version: {}".format(config.getoption("--openshift-version"))


@pytest.fixture(scope="session")
def get_kubeconfig(request):
    if request.config.getoption("--kubeconfig"):
        k8config = request.config.getoption("--kubeconfig")
    elif "KUBECONFIG" in os.environ.keys() and os.environ["KUBECONFIG"]:
        k8config = os.environ["KUBECONFIG"]
    else:
        raise ValueError(
            "A kubeconfig file was not provided. Please provide one either "
            "via the --kubeconfig command option or by setting a KUBECONFIG "
            "environment variable"
        )
    return k8config


@pytest.fixture(scope="session")
def get_kubeconfig_3x(request):
    if request.config.getoption("--kubeconfig-3x"):
        k8config = request.config.getoption("--kubeconfig-3x")
    elif "KUBECONFIG_3X" in os.environ.keys() and os.environ["KUBECONFIG_3X"]:
        k8config = os.environ["KUBECONFIG_3X"]
    else:
        k8config = None
    return k8config


@pytest.fixture(scope="session")
def ocp_smoke_args(request, get_kubeconfig, get_kubeconfig_3x):
    class SmokeArgs:
        def __init__(self):
            self.label_filter = "all"
            self.span = 60
            self.replicas = 5
            self.cluster_config = None
            self.kubeconfig = None
            self.kubeconfig_3x = None

    args_obj = SmokeArgs()
    if request.config.getoption("--filter") not in [[], [""]]:
        args_obj.label_filter = request.config.getoption("--filter")[0].split(",")
    args_obj.span = request.config.getoption("--span")
    args_obj.replicas = request.config.getoption("--replicas")
    args_obj.cluster_config = request.config.getoption("--cluster-config")
    args_obj.kubeconfig = get_kubeconfig
    args_obj.kubeconfig_3x = get_kubeconfig_3x
    return args_obj


@pytest.fixture(scope="session")
def app_ops_args(request, get_kubeconfig, get_kubeconfig_3x):
    class AppOpsArgs:
        def __init__(self):
            self.span = 15
            self.cluster_config = None
            self.num_jenkins_jobs = 5
            self.kubeconfig = None
            self.kubeconfig_3x = None
            self.num_locust_clients = None
            self.locust_hatch_rate = None

    ops_args = AppOpsArgs()
    ops_args.cluster_config = request.config.getoption("--cluster-config")
    ops_args.span = request.config.getoption("--span")
    ops_args.num_jenkins_jobs = request.config.getoption("--num-jenkins-jobs")
    ops_args.num_locust_clients = request.config.getoption("--num-locust-clients")
    ops_args.locust_hatch_rate = request.config.getoption("--locust-hatch-rate")
    ops_args.kubeconfig = get_kubeconfig
    ops_args.kubeconfig_3x = get_kubeconfig_3x
    return ops_args


@pytest.fixture(scope="session")
def load_config_file():
    """ Fixture to load config files and returns a dict"""

    def _load_config_file(config_filename, config_file_type=None):
        # Get file type
        if config_file_type is None:
            _, config_file_type = os.path.splitext(config_filename)
            config_file_type = config_file_type.replace(".", "")

        # load config file
        config = g.load_config(config_filename, config_type=config_file_type)
        return config

    return _load_config_file


@pytest.fixture(scope="session", autouse=True)
def get_openshift_cluster_info(request, load_config_file):
    """ Fixture to get openshift cluster info """
    openshift_tests_log_dir = request.config.getoption("--openshift-tests-log-dir")
    openshift_tests_log_level = request.config.getoption("--openshift-tests-log-level")
    log_to_stdout = request.config.getoption("--log-to-stdout")
    log_name = "ocp_tests_log"

    # Create log dir if logs dir does not exist.
    openshift_tests_log_dir = os.path.abspath(openshift_tests_log_dir)
    if not os.path.exists(openshift_tests_log_dir):
        os.makedirs(os.path.abspath(openshift_tests_log_dir))

    # Define filename with timestamp
    filename = os.path.join(
        openshift_tests_log_dir, ("ocp_tests_log_%s.log" % datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
    )

    g.log = g.create_log(name=log_name, filename=filename, level=openshift_tests_log_level)

    if "true" in log_to_stdout.lower():
        g.add_log(g.log, filename="STDOUT")

    default_ocp_tests_config_file = request.config.getoption("--openshift-default-tests-config")

    if default_ocp_tests_config_file is not None:
        config = load_config_file(default_ocp_tests_config_file)
        g.update_config(config)

    openshift_cluster_config = {}
    openshift_first_master = request.config.getoption("--openshift-first-master")
    openshift_cluster_config["first_master"] = openshift_first_master
    # TODO'S Get master, nodes, OcpAppMgmt instance here.

    g.update_config(openshift_cluster_config)
    g.log.info("openshift tests default configs:\n%s", g.config)


@pytest.fixture(scope="function", autouse=True)
def log_start_test_case(request):
    """ Fixture logging starting and ending of testcases """
    g.log.info("Starting test case: %s", request.node.name)

    def log_end_test_case():
        g.log.info("Ending test case: %s", request.node.name)

    request.addfinalizer(log_end_test_case)


@pytest.fixture(scope="session", autouse=True)
def setup_logger():
    logger = piqe_api_logger(__loggername__)
    return logger
