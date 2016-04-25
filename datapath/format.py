import re

from datapath import constants as c


COMPACT_RESERVED = re.compile(r'([' + re.escape('.:[') + r'])')


def canonical_path(path, is_reversed=False):
    return ''


def compact_path(parts, is_reversed=False):
    if not parts:
        return ''

    str_parts = [_compact_part(*part) for part in parts]
    if is_reversed:
        str_parts = reversed(str_parts)

    path = ''.join(str_parts)

    if path.startswith('.') and not path.startswith('..'):
        return path[1:]

    return path


# ---------------- #
# Internal methods

def _compact_part(key_type, key):
    if key_type & c.TYPE_DICT:
        key = '.' + re.sub(COMPACT_RESERVED, r'\\\1', key)

    elif key_type & c.TYPE_LIST:
        key = ':' + str(key)

    if key_type & c.TRAVERSAL_CHILD:
        return key

    elif key_type & c.TRAVERSAL_RECURSE:
        if key_type & c.TYPE_DICT:
            return '.' + key

        return '..' + key

    raise Exception('WUT?')