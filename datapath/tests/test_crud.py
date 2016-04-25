from unittest import TestCase

from datapath.tests import json_fixture
from datapath.crud import find_path, flatten, unflatten


class TestCrud(TestCase):
    longMessage = True

    def test_find_path(self):
        data = {
            'a': 1,
            'b': [2, 3],
            'c': {
                'b': 4,
                'd': 5,
                'e': 6,
            }
        }

        tests = {
            '*': data.values(),
            'a': [1],
            'b': [[2, 3]],
            'b[0]': [2],
            'b[*]': [2, 3],
            'c.b': [4],
            'c["b"]': [4],
            "c['b']": [4],
            'c.*': [4, 5, 6],
            'c[*]': [4, 5, 6],
            '..b': [[2, 3], 4],
            'c..b': [4],
            'c..*': [4, 5, 6, data['c']],
        }

        for path, expected in tests.iteritems():
            self.assertEqual(sorted(find_path(data, path)), sorted(expected),
                             "We get the expected value for '%s'" % path)

        self.assertEqual(find_path(['good'], '[0]'), ['good'],
                         'Can get a leading list index')

    def test_unflatten(self):
        tests = json_fixture('crud/flatten.json')

        for test in tests:
            self.assertEqual(
                unflatten(test['flat']), test['unflat'],
                "We can unflatten " + test['message'])

    def test_flatten(self):
        tests = json_fixture('crud/flatten.json')

        for test in tests:
            self.assertEqual(
                flatten(test['unflat']), test['flat'],
                "We can flatten " + test['message'])
