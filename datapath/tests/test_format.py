from unittest import TestCase

from datapath.parser import parse_path
from datapath.format import compact_path, canonical_path
from datapath.tests import json_fixture
from datapath import constants as c

class TestFormat(TestCase):
    longMessage = True

    def test_compact_path(self):
        paths = json_fixture('format/compact_paths.json')
        for string_path, expected in paths.iteritems():
            self.assertEqual(
                compact_path(parse_path(string_path)), expected,
                "Converted '%s' to '%s'" % (string_path, expected))

    def test_canonical_path(self):
        paths = json_fixture('format/canonical_paths.json')
        for string_path, expected in paths.iteritems():
            self.assertEqual(
                canonical_path(parse_path(string_path)), expected,
                "Converted '%s' to '%s'" % (string_path, expected))

        with self.assertRaises(Exception):
            canonical_path((c.KEY_WILD | c.TRAVERSAL_CHILD | c.TYPE_LIST, '*'))