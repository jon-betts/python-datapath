import re

from datapath import constants as c

RESERVED_REGEX = re.compile('([' + re.escape(c.CHARS_RESERVED) + '])')


def canonical_path(parts):
    path_string = ''

    for key_type, key in parts:
        if key_type & c.TYPE_DICT:
            if RESERVED_REGEX.search(key):
                key = re.sub(RESERVED_REGEX, r'\\\1', key)

            if key_type & c.KEY_LITERAL:
                key = '"' + key + '"'

        path_string += '[%s]' % key

    return path_string


def compact_path(parts, is_reversed=False):
    parts = [_compact_part(*part) for part in parts]
    if is_reversed:
        parts = reversed(parts)

    path = ''.join(parts)

    if path.startswith('.'):
        return path[1:]

    return path


# ---------------- #
# Internal methods

def _compact_part(key_type, key):
    if key_type & c.TYPE_DICT and RESERVED_REGEX.search(key):
        return '["%s"]' % re.sub(RESERVED_REGEX, r'\\\1', key)

    elif key_type & c.TYPE_LIST:
        return ':%s' % key

    return '.%s' % key
