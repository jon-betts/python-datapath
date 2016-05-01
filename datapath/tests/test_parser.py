from unittest import TestCase

from datapath.parser import parse_path
from datapath import constants as c


class TestParser(TestCase):
    longMessage = True

    def test_parser(self):
        tests = {
            # Dict keys
            '9': ((c.KEY_LITERAL | c.TYPE_DICT, '9'),),
            'a': ((c.KEY_LITERAL | c.TYPE_DICT, 'a'),),
            '.a': ((c.KEY_LITERAL | c.TYPE_DICT, 'a'),),
            '["a"]': ((c.KEY_LITERAL | c.TYPE_DICT, 'a'),),
            "['a']": ((c.KEY_LITERAL | c.TYPE_DICT, 'a'),),
            "['a', 'b']": ((c.KEY_SLICE | c.TYPE_DICT, ('a', 'b')),),

            '*': ((c.KEY_WILD | c.TYPE_DICT, '*'),),
            '.*': ((c.KEY_WILD | c.TYPE_DICT, '*'),),
            '[*]': ((c.KEY_WILD | c.TYPE_DICT, '*'),),
            '["a", "b"]': ((c.KEY_SLICE | c.TYPE_DICT, ('a', 'b')),),

            # List indices
            ':*': ((c.KEY_WILD | c.TYPE_LIST, '*'),),
            ':0': [(c.TYPE_LIST | c.KEY_LITERAL, 0), ],
            '[0]': [(c.TYPE_LIST | c.KEY_LITERAL, 0), ],
            ':-1': [(c.TYPE_LIST | c.KEY_LITERAL, -1), ],

            '[-1]': [(c.TYPE_LIST | c.KEY_LITERAL, -1), ],
            '[:]': [(c.TYPE_LIST | c.KEY_SLICE, slice(None, None, None)), ],
            '[::]': [(c.TYPE_LIST | c.KEY_SLICE, slice(None, None, None)), ],
            '[0:]': [(c.TYPE_LIST | c.KEY_SLICE, slice(0, None, None)), ],
            '[:0]': [(c.TYPE_LIST | c.KEY_SLICE, slice(None, 0, None)), ],
            '[::0]': [(c.TYPE_LIST | c.KEY_SLICE, slice(None, None, 0)), ],
            ':0:0': [
                (c.TYPE_LIST | c.KEY_LITERAL, 0),
                (c.TYPE_LIST | c.KEY_LITERAL, 0)
            ],

            ':0,1,2': [(c.TYPE_LIST | c.KEY_SLICE, (0, 1, 2)), ],
            '[0,1,2]': [(c.TYPE_LIST | c.KEY_SLICE, (0, 1, 2)), ],
            ':0, 1, 2': [(c.TYPE_LIST | c.KEY_SLICE, (0, 1, 2)), ],
            '[0, 1, 2]': [(c.TYPE_LIST | c.KEY_SLICE, (0, 1, 2)), ],

            # Recusing
            '..a': ((c.TRAVERSAL_RECURSE | c.KEY_LITERAL | c.TYPE_DICT, 'a'),),
            '..*': ((c.TRAVERSAL_RECURSE | c.KEY_WILD | c.TYPE_DICT, '*'),),
            '..[9]': ((c.TRAVERSAL_RECURSE | c.KEY_LITERAL | c.TYPE_LIST, 9),),
            '..9': ((c.TRAVERSAL_RECURSE | c.KEY_LITERAL | c.TYPE_DICT, '9'),),
            '..:9': ((c.TRAVERSAL_RECURSE | c.KEY_LITERAL | c.TYPE_LIST, 9),),
            '..["a"]': (
                (c.TRAVERSAL_RECURSE | c.KEY_LITERAL | c.TYPE_DICT, 'a'),),
            '..[*]': ((c.TRAVERSAL_RECURSE | c.KEY_WILD | c.TYPE_DICT, '*'),),
        }

        for path_string, path_parts in tests.iteritems():
            parts = parse_path(path_string)

            self.assertEqual(
                [p[1] for p in parts], [p[1] for p in path_parts],
                "We get the keys we expect for path '%s'" % path_string)

            for pos, (part_type, expected_type) in enumerate(zip(
                    [p[0] for p in parts], [p[0] for p in path_parts])):
                self.assertEqual(
                    c.describe(part_type), c.describe(expected_type),
                    "Got expected key type at position '%s' for path '%s'" % (
                        pos, path_string
                    ))

    def test_parser_splitting(self):
        tests = {
            'a.b': ['a', 'b'],
            'a[6]': ['a', 6],
            'a\\.b': ['a.b'],
            'a\\.b.c': ['a.b', 'c'],
            '["["]': ['['],
            'a.*': ['a', '*'],
            'a[*]': ['a', '*'],
            'a..b': ['a', 'b'],
            '\\[\\]': ['[]'],
            '["[]"]': ['[]']
        }

        for path_string, keys in tests.iteritems():
            got_keys = [key for _, key in parse_path(path_string)]

            self.assertEqual(got_keys, keys,
                             "Correctly get the parts for '%s'" % path_string)
