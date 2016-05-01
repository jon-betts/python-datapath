from datapath import constants as c
from datapath.format import compact_path
from datapath.util import BranchingList, guess_type


def walk(data, function, root=None, parent=None, key=None, path=None):
    if root is None:
        root = data

    if path is None:
        path = BranchingList()

    data_type = guess_type(data)

    instruction = function(
        data=data, data_type=data_type, parent=parent, key=key, path=path)

    if instruction != c.WALK_CONTINUE:
        return instruction

    if data_type == c.TYPE_LEAF:
        return
    elif data_type == c.TYPE_DICT:
        items = data.iteritems()
    elif data_type == c.TYPE_LIST:
        items = enumerate(data)

    # Prevent changing size:
    items = tuple(items)

    for key, item in items:
        instruction = walk(
            # Things that don't change
            function=function, root=root,

            # Things that do
            data=item, key=key, parent=data,
            path=path.add((c.KEY_LITERAL | data_type, key))
        )

        if instruction == c.WALK_PRUNE:
            break

        if instruction == c.WALK_TERMINATE:
            return c.WALK_TERMINATE


def walk_path(data, function, path_parts,
              on_missing=c.ON_MISSING_CONTINUE,
              on_mismatch=c.ON_MISMATCH_CONTINUE,
              root=None):

    context = {
        'root': root or data,
        'function': function,
        'path_parts': path_parts,
        'on_mismatch': on_mismatch,
        'on_missing': on_missing,
    }

    return _walk_path(context, data=data, path_pos=0, parent=None, key=None,
                      path=BranchingList())


# ---------------- # -------------------------------------------------------- #
# Internal methods #
# ---------------- #

def _walk_path(context, data, path_pos, parent, key, path):
    data_type = guess_type(data)

    instruction = context['function'](
        # Things which change all the time
        data=data, data_type=data_type, path_pos=path_pos,
        parent=parent, key=key, path=path,

        # Things we calculate to be nice
        terminal=path_pos == len(context['path_parts']),

        **context)

    if instruction != c.WALK_CONTINUE:
        return instruction

    # We've run out of path
    if path_pos >= len(context['path_parts']):
        return

    key_type, key = context['path_parts'][path_pos]

    if key_type & c.TRAVERSAL_RECURSE:
        return _path_recursion(
            data=data, parent=parent, path=path, path_pos=path_pos,
            context=context)

    elif not key_type & data_type:
        if context['on_mismatch'] == c.ON_MISMATCH_FAIL:
            raise ValueError('Expected %s but found %s at %s: %s' % (
                c.STRINGS[key_type & c.TYPE_MASK],
                c.STRINGS[data_type],
                data,
                compact_path(context['path_parts'])
            ))

        elif context['on_mismatch'] == c.ON_MISMATCH_CONTINUE:
            return c.WALK_CONTINUE
        else:
            raise Exception('wut?')

    # It's a super mad recursion into the data structure

    # A literal, we know exactly where to go
    elif key_type & c.KEY_LITERAL:
        try:
            data[key]
        except (KeyError, IndexError):
            if context['on_missing'] == c.ON_MISSING_CONTINUE:
                return
            elif context['on_missing'] == c.ON_MISSING_CREATE:
                data = _auto_fill(data, data_type, key,
                                  context['path_parts'], path_pos)

        return _walk_path(context, data=data[key], key=key, parent=data,
                          path=path.add((c.KEY_LITERAL | data_type, key)),
                          path_pos=path_pos + 1)

    elif key_type & (c.KEY_WILD | c.KEY_SLICE):
        # A wild key
        if key_type & c.KEY_WILD:
            if data_type & c.TYPE_LIST:
                keys = xrange(len(data))
            elif data_type & c.TYPE_DICT:
                keys = data.iterkeys()
            else:
                raise ValueError('Unknown sub-object type')

        # Then it's a slice
        else:
            if data_type & c.TYPE_LIST and isinstance(key, slice):
                stop = max(key.stop or 0, len(data))
                keys = xrange(*key.indices(stop))
            else:
                # Literal values
                keys = key

        for key in keys:
            # TODO! - Some copy paste here from above.
            try:
                data[key]
            except (KeyError, IndexError):
                if context['on_missing'] == c.ON_MISSING_CONTINUE:
                    continue
                elif context['on_missing'] == c.ON_MISSING_CREATE:
                    data = _auto_fill(data, data_type, key,
                                      context['path_parts'], path_pos)
                else:
                    raise

            instruction = _walk_path(
                context, data=data[key], key=key,
                parent=data, path_pos=path_pos + 1,
                path=path.add((c.KEY_LITERAL | data_type, key)))

            if instruction == c.WALK_PRUNE:
                break

            if instruction == c.WALK_TERMINATE:
                return c.WALK_TERMINATE

    else:
        raise Exception('Bad key type')


def _auto_fill(data, data_type, key, path_parts, path_pos):
    if path_pos >= len(path_parts) - 1:
        next_type = c.TYPE_LEAF
    else:
        next_type, _ = path_parts[path_pos + 1]

    next_factory = c.TYPE_CODE_TO_TYPE[c.TYPE_MASK & next_type]

    # Auto extend lists if required
    if data_type & c.TYPE_LIST:
        if len(data) <= key:
            data.extend([next_factory() for _ in xrange(1 + key - len(data))])

    else:
        data[key] = next_factory()

    return data


def _path_recursion(data, parent, path, path_pos, context):
    # Generate a mini path to look for
    path_part = context['path_parts'][path_pos]
    search_path = ((path_part[0] ^ c.TRAVERSAL_RECURSE, path_part[1]),)

    # First find all the eligible entities

    worklist = []

    # The general search will find all entities
    def _general_search(path, **kwargs):

        # The path aware search will search the search path for eligible
        # items to resume the main path walk
        def _back_to_walk_path(parent, key, data, data_type, **_):
            if parent is None and key is None:
                return

            worklist.append(
                dict(data=data, parent=parent, key=key,
                     path=path.add((c.KEY_LITERAL | data_type, key))))

        walk_path(kwargs['data'], _back_to_walk_path, search_path)

    walk(data=data,
         function=_general_search,
         parent=parent, key=None, path=path)

    # Now start walking through the paths in them. We do this so we don't
    # create new items as we are searching and recurse infinitely

    path_pos += 1

    for item in worklist:
        _walk_path(path_pos=path_pos, context=context, **item)
