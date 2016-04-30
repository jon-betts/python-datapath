from datapath.parser import parse_path
from datapath import crud
from datapath import constants as c
from datapath.walk import walk_path

class DataPathDict(dict):
    # ----------- #
    # Crud access

    def find(self, path_string):
        return crud.find_path(self, path_string)

    def get(self, path_string, default=None):
        return crud.get_path(self, path_string, default)

    def set(self, path_string, value):
        return crud.set_path(self, path_string, value)

    def flatten(self):
        return crud.flatten(self)

    def merge(self, other):
        for path_string, value in crud.flatten(other).iteritems():
            self.set(path_string, value)

        return self

    def apply(self, path, function):
        walk_path(self, function, parse_path(path))

        return self

    @classmethod
    def unflatten(cls, flat_dict):
        return DataPathDict(crud.unflatten(flat_dict))

    # ------------- #
    # Magic methods

    def __getitem__(self, item):
        if isinstance(item, list):
            path_parts = parse_path(item[0])

            for key_type, _ in path_parts:
                if key_type & (c.KEY_WILD | c.KEY_SLICE | c.TRAVERSAL_RECURSE):
                    return crud.find_path_parts(self, path_parts)

            default = None
            if len(item) > 1:
                default = item[1]

            return crud.get_path_parts(self, path_parts, default=default)

        return super(DataPathDict, self).__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, list):
            return crud.set_path(self, key[0], value)

        return super(DataPathDict, self).__setitem__(key, value)
