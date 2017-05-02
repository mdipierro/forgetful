# Forgetful

It is a minimalist caching library. Think of memcache or redis. It exposes an API similar to a python dictionary by only keeps in memory the most recently accessed n elements. Access time is about 2 micro seconds per get/set/forget. 

The running time is that of a hash table and therefore close O(1). It is independent on the number of the elements stored. It is implemented as a doubly linked list plus a hash table that maps keys into nodes of the list. The list nodes store values. The list is aways sorted in chronological order. When an element it accessed (get or set), the key is looked up in the hash table, the corresponding node is removed and moved at the end of the list, in constant time.

Example

```
>>> from forgetful import Forgetful
>>> d = Forgetful(100)
>>> for x in range(10000):
        d[x] = x
>>> print(d[9999])
9999
>>> assert len(d) == 100
>>> del d[999]
```

It can also be run as service with the built in xmlrpc server:

```
$ python forgetful.py -d 0.0.0.0:8081
```

```
>>> import xmlrpc
>>> proxy = xmlrpclib.ServerProxy("http://localhost:8081", allow_none=True)
>>> proxy.set('a',10)
>>> proxy.get('a')
10
>>> proxy.add('a', 1)
11
>>> proxy.forget('a')
```
