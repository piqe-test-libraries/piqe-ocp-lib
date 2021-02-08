import pytest

from openshift.dynamic.resource import ResourceInstance


@pytest.fixture(scope="session")
def response_factory():
    def factory(client, body):
        return ResourceInstance(client, body)
    return factory
