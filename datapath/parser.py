from datapath import constants as c

START_TOKEN = '.:['


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
        # It's a recursion
        if next_char == '.':
            start, key = _find_next(path_string, start + 1, START_TOKEN)
            return _key_type(key, c.TYPE_DICT | c.TRAVERSAL_RECURSE), key, start
        else:
            start, key = _find_next(path_string, start, START_TOKEN)
            return _key_type(key, c.TYPE_DICT), key, start

    elif char == ':':
        start, key = _find_next(path_string, start, START_TOKEN)
        key_type = _key_type(key, c.TYPE_LIST)

        if not key_type & c.KEY_WILD:
            try:
                key = int(key)
            except ValueError:
                raise Exception('wut?')

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

        if key.isdigit():
            return c.TYPE_LIST | c.KEY_LITERAL, int(key), start + 1
        elif key == c.CHARS_WILD:
            return c.TYPE_LIST | c.TYPE_DICT | c.KEY_WILD, key, start + 1
        else:
            return c.TYPE_DICT | c.KEY_LITERAL, key, start + 1

    raise ValueError("Unexpected char '%s' at '%s'" % (char, start))


def parse_path(path_string):
    parts = []

    start, key = _find_next(path_string, 0, START_TOKEN)
    if start != 0:
        parts.append((_key_type(key, c.TYPE_DICT | c.TRAVERSAL_CHILD), key))

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
            key_type |= c.TRAVERSAL_CHILD

        parts.append((key_type, key))

    return parts
