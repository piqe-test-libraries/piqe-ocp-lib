# PIQE Test Libraries - PIQE OCP Library

**This is a work in progress and not recommended for consumption at this point.**

The PIQE test libraries are a collection of Python libraries that enable you to interact with OpenShift instances.


## Requirements

* A target OpenShift environment.
* A Kubeconfig file that provides access to the target environment.
* An OpenShift OC client that matches the version of your environment

## Getting started
The following steps will prepare your environment for executing or developing tests.

#### Prepare the environment

Eventually a Python Package will be available, but for now, simply clone this repository.

    git clone https://github.com/piqe-test-libraries/piqe-ocp-lib.git

Change directory to piqe-ocp-lib and create a virtual environment.

    python3 -m venv scenario

Enter the virtual environment, export the environment variables and performn a pip install.

    source scenario/bin/activate
    export KUBECONFIG=/vagrant/auth/ocp43/kubeconfig
    pip install .

At this point, your environment is prepared. Verify that you can connect to your OpenShift instance.

    $ oc cluster-info
    Kubernetes master is running at https://api.<yourdomain>.com:6443

#### Try running a test

The API library resides under piqe_ocp_lib/api/resources, and the corresponding tests reside under piqe_ocp_lib/tests/resources.

Run the test_ocp_base tests

    pytest -sv piqe_ocp_lib/tests/resources/test_ocp_base.py

Results similar to those shown below should be presented.

    ====================================== test session starts ======================================
    platform linux -- Python 3.7.6, pytest-5.4.1, py-1.8.1, pluggy-0.13.1 -- /vagrant/piqe-test-libraries/piqe-ocp-lib/scenario/bin/python3
    cachedir: .pytest_cache
    OpenShift version: latest
    rootdir: /vagrant/piqe-test-libraries/piqe-ocp-lib
    plugins: dependency-0.5.1, forked-1.1.3, xdist-1.31.0
    collected 1 item

    piqe-ocp-lib/tests/resources/test_ocp_base.py::TestOcpBase::test_init 2020-03-18 16:00:03,318 INFO (get_openshift_cluster_info) openshift tests default configs:
    {'first_master': None}
    2020-03-18 16:00:03,318 INFO (log_start_test_case) Starting test case: test_init
    2020-03-18 16:00:03,883 - [INFO] - piqe_api_logger - test_ocp_base@test_init:25 - The obtained version is: 4.3.0
    PASSED2020-03-18 16:00:03,884 INFO (log_end_test_case) Ending test case: test_init


    ======================================= 1 passed in 0.96s =======================================

#### Cluster Config

Some task-level APIs or tests require the use of a cluster_config yaml file that describes 
the layout of the cluster and the resources being deployed. You can either specify the file using a command
line flag or set the variable `PIQE_OCP_LIB_CLUSTER_CONF` variable to the path. 

For reference you can refer to the one used in our tests [here](piqe_ocp_lib/tests/config/smoke_ocp_config.yaml)

## Release process

We're maintaining a log of changes for every release. Semantic versioning and Keep a Changelog were chosen as standards. You can find more information about both standards [here](CHANGELOG.md).

This library shall be automatically published to Pypi following the steps below:
1. Update `CHANGELOG.md` with the new changes (Keep a Changelog);
2. Bump your package version with `poetry version major.minor.patch` (Semantic Versioning);
3. Open a PR with these two changes above;
4. Manually create a GitHub release;
5. Successful CI will publish.

### Further improvements

We're currently not running any tests in our CI phase due to some limitations. We should target improving this and remove this burden from developers.
