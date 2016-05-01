from datapath import ddict
from datapath import constants as c
from datapath.parser import parse_path, _find_next

data = {
    'a': {
        'b': {},
        'c': [
            {'b': {}}
        ]
    },
    'b': {}
}

data = ddict(data)

data[['..["c", "b"]']] = 'T'

print data