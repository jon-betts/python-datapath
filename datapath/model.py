import datapath.constants
from datapath.parser import parse_path
from datapath.format import canonical_path, compact_path
from datapath import crud


class Path(object):
    def __init__(self, path_string):
        self.path_string = path_string
        self.parts = parse_path(path_string)

    def canonical(self):
        return canonical_path(self.parts)

    def compact(self):
        return compact_path(self.parts)

    def get(self, data, default=None):
        return crud.get_path_parts(data, self.parts, default)

    def find(self, data, on_mismatch=datapath.constants.ON_MISMATCH_CONTINUE):
        return crud.find_path_parts(data, self.parts)

    def set(self, data, value):
        return crud.set_path_parts(data, self.parts, value)

    def __repr__(self):
        return self.compact()


class AwareDict(object):
    @classmethod
    def unflatten(cls, flat_dict):
        return AwareDict(crud.unflatten(flat_dict))

    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data

    def find(self, path_string):
        return crud.find_path(self.data, path_string)

    def get(self, path_string, default=None):
        return crud.get_path(self.data, path_string, default)

    def set(self, path_string, value):
        return crud.set_path(self.data, path_string, value)

    def flatten(self):
        return crud.flatten(self.data)


class EnabledDict(AwareDict):
    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __repr__(self):
        return self.data.__repr__()
