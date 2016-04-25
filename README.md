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
 

Compact paths
-------------

The `datapath` library supports compact paths which cut a small amount of the 
verboseness of the full JSONPath spec. A number of simplifying assumptions 
are made:
  
 * All paths are local
 * 'Naked' paths without a prefix are assumed to be dict keys
 * Bracked paths are assumed to be on the local object
 
Examples:

| JSONPath | `datapath` equivalents |
| -------- | -----------------------|
| $.a      | a, .a, ["a"], ['a']    |
| $.[7]    | [7]                    |
| $.*      | *, .*                  |
| $..a     | ..a                    |
| @..a     | ..a                    |
| @.a      | a, .a, ["a"], ['a']    |

The JSONPath spec suggest `'@.'` for local anchoring and `'$.'` for root 
anchoring. Where anchoring is not specified or relevant `datapath` allows the 
omission of the leading identifiers for example:

| JSONPath | `datapath` compact  |
| -------- | ------------------- |
| $.a, | a |                     |
| @.a | a  |                     |
| $.['a']  | a                   |
| @.['a']  | a                   |
| $.["a"]  | a                   |
| @.["a"]  | a                   |

**NOTE!** - Currently `datapath` doesn't allow anchoring markers

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

 * List slices
 * Selectors beyond `'*'` - no ability to do things like `book[author='lily']`
 * Anchoring specifications: `'@.'`, `'$.'`

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

# Retrieve a value deeply nested
print a[['store.book:0.price']]

# Retrieve a value that doesn't exist yet without an issue (with a default)
print a[['store.book:10.price', 0]]

# Set a value that doesn't exist yet
a[['store.book:2.price']] = 8.99

# Set all book categories at once
a[['store.book:*.category']] = 'fiction'

# The price of everything
print a[["..price"]]

# The price of everything in the store
print a[["store..price"]]
```
    
Known issues
------------

 * This library doesn't work, and using it is a fools errand
 * Attempting to set recursive paths (e.g. 'a..b') doesn't work
 * Recursive paths in general are likely to have undefined behavior
  
