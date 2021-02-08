import pytest

from openshift.dynamic.resource import ResourceInstance


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)


@pytest.fixture(scope="session")
def response_factory():
    def foo(client, body):
        return ResourceInstance(client, body)
    return foo
