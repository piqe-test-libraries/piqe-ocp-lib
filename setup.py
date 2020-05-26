from setuptools import setup

from piqe_ocp_lib import __version__

setup(
    name="piqe-ocp-lib",
    version=__version__,
    author="PIQE Libraries Team",
    author_email="amacmurr@redhat.com",
    description="PIQE OpenShift Python Libraries.",
    url="https://github.com/piqe-test-libraries/piqe-ocp-lib.git",
    packages=setuptools.find_packages(),
    install_requires=[
        "openshift",
        "pytest-dependency",
        "pytest-xdist",
        "locust",
        "glusto@git+git://github.com/loadtheaccumulator/glusto.git"
        "@python3_port4#egg=glusto"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
    ],
)
