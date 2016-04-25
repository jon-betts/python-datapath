import json
import pkg_resources
import os.path


def json_fixture(fixture_name):
    path = os.path.join('fixtures/' + fixture_name)

    with pkg_resources.resource_stream('datapath.tests', path) as fh:
        return json.load(fh)