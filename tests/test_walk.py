from unittest import TestCase

from datapath import constants as c
from datapath.util import guess_type


class TestWalk(TestCase):
    longMessage = True

    def test_guess_type(self):
        tests = [
            [tuple(), c.TYPE_LIST],
            [list(), c.TYPE_LIST],
            [dict(), c.TYPE_DICT],
            ['', c.TYPE_LEAF],
            [None, c.TYPE_LEAF],
            [6, c.TYPE_LEAF]
        ]

        for obj, obj_type in tests:
            self.assertEqual(
                guess_type(obj), obj_type,
                "We can correctly get the type for '%s'" % str(obj))
