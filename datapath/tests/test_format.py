from unittest import TestCase

from datapath.parser import parse_path
from datapath.format import compact_path
from datapath.tests import json_fixture


class TestFormat(TestCase):
    longMessage = True

    def test_compact_path(self):
        paths = json_fixture('format/compact_paths.json')
        for string_path, expected in paths.iteritems():
            self.assertEqual(
                compact_path(parse_path(string_path)), expected,
                "Converted '%s' to '%s'" % (string_path, expected))