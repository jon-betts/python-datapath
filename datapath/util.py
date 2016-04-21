from datapath import constants as c


class BranchingList(object):
    def __init__(self, value=None, parent=None):
        if parent is None:
            if value:
                self.length = 1
                self.data = ((), value)

            else:
                self.length = 0
                self.data = ()

        else:
            self.length = parent.length + 1
            self.data = (parent.data, value)

    def add(self, value):
        return BranchingList(value, self)

    def __reversed__(self):
        data = self.data
        while data:
            yield data[1]
            data = data[0]

    def __iter__(self):
        return reversed([x for x in reversed(self)])

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if key < 0:
            recurse = 0 - key
        else:
            recurse = self.length - key

        data = self.data

        while recurse:
            recurse -= 1

            if recurse <= 0:
                return data[1]
            else:
                data = data[0]

        raise IndexError()

    @classmethod
    def from_iterable(cls, iterable):
        nester = BranchingList()
        for item in iterable:
            nester = nester.add(item)

        return nester


def guess_type(obj):
    return c.TYPE_TO_TYPE_CODE.get(type(obj), c.TYPE_LEAF)