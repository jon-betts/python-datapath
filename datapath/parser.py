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


def parse_path(path_string):
    parts = []

    start, key = _find_next(path_string, 0, START_TOKEN)
    if start != 0:
        parts.append((_key_type(key, c.TYPE_DICT), key))

    while start < len(path_string):
        char = path_string[start]
        next_char = path_string[start + 1]

        start += 1

        # Dot notation
        if char == '.':
            if next_char == '.':
                start, key = _find_next(path_string, start + 1, START_TOKEN)
                parts.append((_key_type(key, c.TYPE_DICT | c.KEY_RECURSE), key))
            else:
                start, key = _find_next(path_string, start, START_TOKEN)
                parts.append((_key_type(key, c.TYPE_DICT), key))

        elif char == ':':
            start, key = _find_next(path_string, start, START_TOKEN)
            key_type = _key_type(key, c.TYPE_LIST)
            if not key_type & c.KEY_WILD:
                key = int(key)

            parts.append((key_type, key))

        # In brackets
        elif char == '[':
            # Quoted in brackets
            if next_char in '"\'':
                start, key = _find_next(path_string, start + 1, next_char)

                # Skip the ending quote
                start += 1
                if path_string[start] != ']':
                    raise ValueError('Expected ] at %s' % start)

                parts.append((c.TYPE_DICT | c.KEY_LITERAL, key))

            # Raw in brackets
            else:
                start, key = _find_next(path_string, start, ']')

                if key.isdigit():
                    parts.append((c.TYPE_LIST | c.KEY_LITERAL, int(key)))
                elif key == c.CHARS_WILD:
                    parts.append((c.TYPE_LIST | c.TYPE_DICT | c.KEY_WILD, key))
                else:
                    parts.append((c.TYPE_DICT | c.KEY_LITERAL, key))

            # Skip the bracket to the next char
            start += 1
        else:
            raise ValueError("Unexpected char '%s' at '%s'" % (char, start))

    return parts