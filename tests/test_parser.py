from unittest import TestCase

from datapath.parser import parse_path
from datapath import constants as c


class TestParser(TestCase):
    longMessage = True

    def test_parser_splitting(self):
        tests = {
            'a': ['a'],
            '.a': ['a'],
            '[a]': ['a'],
            '["a"]': ['a'],
            '[9]': [9],
            'a.b': ['a', 'b'],
            'a[6]': ['a', 6],
            'a\\.b': ['a.b'],
            'a\\.b.c': ['a.b', 'c'],
            '["["]': ['['],
            'a.*': ['a', '*'],
            'a[*]': ['a', '*']
        }

        for path_string, keys in tests.iteritems():
            got_keys = [key for _, key in parse_path(path_string)]

            self.assertEqual(got_keys, keys,
                             "Correctly get the parts for '%s'" % path_string)

    def test_parser_typing(self):
        tests = {
            'a': ('a', c.TYPE_DICT | c.KEY_LITERAL),
            '.a': ('a', c.TYPE_DICT | c.KEY_LITERAL),
            '["a"]': ('a', c.TYPE_DICT | c.KEY_LITERAL),
            "['a']": ('a', c.TYPE_DICT | c.KEY_LITERAL),
            '[1]': (1, c.TYPE_LIST | c.KEY_LITERAL),
            '*': ('*', c.KEY_WILD | c.TYPE_DICT | c.TYPE_LIST),
            '.*': ('*', c.KEY_WILD | c.TYPE_DICT | c.TYPE_LIST),
            '[*]': ('*', c.KEY_WILD | c.TYPE_DICT | c.TYPE_LIST),
            '..a': ('a', c.KEY_RECURSE | c.KEY_LITERAL | c.TYPE_DICT),
        }

        for path, (key, key_type) in tests.iteritems():
            path_parts = parse_path(path)
            got_type, got_key = path_parts[0]

            self.assertEqual(len(path_parts), 1, 'Got one part for %s' % path)

            self.assertEqual(got_key, key,
                             'Got the expected key for %s' % path)
            self.assertEqual(got_type, key_type,
                             'Got the expected type for %s' % path)