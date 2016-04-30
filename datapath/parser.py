from datapath import constants as c

START_TOKEN = '.:['


def parse_path(path_string):
    parts = []

    start, key = _find_next(path_string, 0, START_TOKEN)
    if start != 0:
        parts.append((_key_type(key, c.TYPE_DICT), key))

    while start < len(path_string):
        char = path_string[start]
        char_plus_1 = path_string[start + 1]

        if char == '.' and char_plus_1 == '.':
            char_plus_2 = path_string[start + 2]
            if char_plus_2 in '[:':
                # Plus 2 to skip over the dots and parse again
                key_type, key, start = _capture_next(path_string, start + 2)
            else:
                # We re-use the dot detection on the last dot to trigger compact
                # dict key format parsing
                key_type, key, start = _capture_next(path_string, start + 1)

            key_type |= c.TRAVERSAL_RECURSE

        else:
            key_type, key, start = _capture_next(path_string, start)

        parts.append((key_type, key))

    return parts


# ---------------- # -------------------------------------------------------- #
# Internal methods #
# ---------------- #

def _find_next(string, pos, stop_chars):
    escaping = False
    out_string = ''

    for offset, char in enumerate(string[pos:]):
        if char == '\\':
            escaping = True

        elif escaping:
            escaping = False
            out_string += char

        elif char in stop_chars:
            return offset + pos, out_string

        else:
            out_string += char

    return len(string), out_string


def _key_type(string, key_type=0):
    if string == c.CHARS_WILD:
        return key_type | c.KEY_WILD

    return key_type | c.KEY_LITERAL


def _capture_next(path_string, start):
    char = path_string[start]
    next_char = path_string[start + 1]
    start += 1

    # Dot notation or ...
    if char == '.':
        start, key = _find_next(path_string, start, START_TOKEN)
        return _key_type(key, c.TYPE_DICT), key, start

    elif char == ':':
        start, key = _find_next(path_string, start, START_TOKEN)
        key_type, key = _parse_list_index(key)
        return key_type, key, start

    # In brackets
    elif char == '[':
        # Quoted in brackets
        if next_char in '"\'':
            start, key = _find_next(path_string, start + 1, next_char)

            # Skip the ending quote
            start += 1
            if path_string[start] != ']':
                raise ValueError('Expected ] at %s' % start)

            return c.TYPE_DICT | c.KEY_LITERAL, key, start + 1

        # Raw in brackets
        start, key = _find_next(path_string, start, ']')

        if key == c.CHARS_WILD:
            return c.TYPE_DICT | c.KEY_WILD, key, start + 1
        else:
            key_type, key = _parse_list_index(key)
            return key_type, key, start + 1

    raise ValueError("Unexpected char '%s' at '%s'" % (char, start))


def _parse_list_index(string):
    if string == c.CHARS_WILD:
        return c.TYPE_LIST | c.KEY_WILD, string

    try:
        return c.TYPE_LIST | c.KEY_LITERAL, int(string)

    except ValueError:
        if ':' in string:
            parts = [None if i is '' else int(i) for i in string.split(':')]
            return c.TYPE_LIST | c.KEY_SLICE, slice(*parts)

        elif ',' in string:
            return (c.TYPE_LIST | c.KEY_SLICE,
                    tuple(int(i) for i in string.split(',')))

    raise ValueError("Cannot parse list index '%s'" % string)
