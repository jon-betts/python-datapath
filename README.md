# python-datapath

XPath like functions for python data structures to get and *set* values based
on a data description string.

Inspired by, but not completely compliant with the JSONPath specification
suggested at http://goessner.net/articles/JsonPath/

Why should I use this library?
------------------------------

datapath lets you:

 * Get values from deeply nested structures without caring if any of the 
 intermediate keys exist
 * Set values into data structures and have all intermediate values created 
 for you
 

Compact paths
-------------

The datapath library supports compact paths which cut a small amount of the 
verboseness of the full JSONPath spec.  

The JSONPath spec suggest '@.' for local anchoring and '$.' for root anchoring.
Where anchoring is not specified or relevant datapath allows the omission of
the leading identifiers for example:

| JSONPath | datapath |
| $.a | a, .a, ["a"], ['a'] | 


Compliance levels
-----------------

The datapath library does not support


Enough talking!
---------------

    from datapath.crud import get_path, find_path, set_path
    
    data = {
        'a': ['hello', 'world'],
        'b': 5
    }
        
    print get_path(data, 'a')     # ['hello', 'world']
    print get_path(data, 'a[0]')  # 'hello'
    
    find_path(data, '*.*')      # [['hello', 'world'], 5]
    
    set_path({}, 'not_there[4].more', 'value')
    # {'not_there': [None, None, None, {'more': 'value'}]}
    