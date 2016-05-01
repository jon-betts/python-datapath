# python-datapath

Use [JSONPath](http://goessner.net/articles/JsonPath/)
like strings  to **get and set** values in a deeply nested data structure 
with graceful retrieval if the structure does not exist and
[autovivification](https://en.wikipedia.org/wiki/Autovivification) when setting
values.

Inspired by, but not completely compliant with the [JSONPath specification]
(http://goessner.net/articles/JsonPath/)

Why should I use this library?
------------------------------

**YOU REALLY SHOULDN'T** - This is nowhere near ready to be used yet!

`datapath` lets you:

 * Get values from deeply nested structures without caring if any of the 
 intermediate keys exist
 * Set values into data structures and have all intermediate values created 
 for you
 * Turn deeply nested structures into flat dicts and back

Enough talking!
---------------

```python
from datapath import ddict

a = ddict({
    'store': {
        'book': [
            {
                'title': 'Sayings of the Century',
                'price': 8.95
            }
        ]
    },
    'bicycle': {
        'color': 'red',
        'price': 19.95
    }
})

# Retrieve a value deeply nested value

# ...by using it as a normal dict
print a['store']['book'][0]['price']  # Not very safe
print a.get('store', {}).get('book', [{}])[0].get('price')  # Much safer

# ... or using datapath
print a[['store.book:0.price']]

# Retrieve a value that doesn't exist yet without an issue (with a default)
print a[['store.book:10.price', 0]]

# Set values on objects that don't yet exist
a[['store.book:2.price']] = 8.99
a[['new.here:3.escaped\\.dot']] = 'All intermediate structures created'

# Set all book categories at once
a[['store.book:*.category']] = 'fiction'

# The price of everything
print a[["..price"]]

# The price of everything in the store
print a[["store..price"]]
```

Compact paths
-------------

The `datapath` library supports compact paths which cut a small amount of the 
verboseness of the full JSONPath spec. A number of simplifying assumptions 
are made:
  
 * All paths are local
 * 'Naked' paths without a prefix are assumed to be dict keys
 * Bracketed paths are assumed to be on the local object
 
You can mix and match compact paths or JSON Paths in the same path.
 
| Action                  | Compact path | JSON Path     |
| ----------------------- | ------------ | ------------- |
| Dict key                | `.a`, `a`    | `$["a"]`      |
| Dict key wild           | `.*`, `*`    | `$[*]`        |
| Dict key slice          | `["a", "b"]` | `$["a", "b"]` |
| Recurse to dict key     | `..a`        | `$..a`        |
| Recurse to any dict key | `..*`        | `$..*`        |
| List key                | `:3`, `[3]`  | `$[3]`        |
| List key wild           | `:*`         | n/a           |
| List slice              | `[0:10:2]`   | `$[0:10:2]`   |
| List slice (range)      | `[0,2,-1]`   | `$[0,2,-1]`   |
| Recurse to list key     | `..:0`       | n/a           |
 
### Anchoring

The JSONPath spec suggest `'@.'` for local anchoring and `'$.'` for root 
anchoring. Where anchoring is not specified or relevant `datapath` allows the 
omission of the leading identifiers.

**NOTE!** - Currently `datapath` parses anchors, but does nothing with them.

Escaping
--------

You can set a key with a dot, or any other reserved character by escaping it:

```python
from datapath.crud import get_path
 
print get_path('a\\.b', {'a.b' : 5})  # 5!
```

Compliance levels
-----------------

The `datapath` library does not support the following parts of JSONPath at the
moment:

 * Selectors beyond `'*'` or slices
 * No ability to do things like `book[author='lily']`

Known issues
------------

 * This library doesn't work, and using it is a fools errand
 * Setting recursive paths is a bit wonky
   ** Sometimes it's accurate but counter intuitive
  
