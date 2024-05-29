# REEM

Author: Trishul Nagenalli and Kris Hauser

## About

REEM (Redis Extendable Efficient Middleware) is a middleware package for communication across distributed systems (e.g., robots) using a centralized Redis database. It is designed to be a single-package solution for passing information anywhere in a system while emphasizing ease of use and efficiency.

- REEM is easy to use.  You can read or write data from the database using a nested data structure that feels almost like working with native Python dictionaries, lists, strings, numbers, and Numpy arrays.  If you feel ReJSON is a little clumsy, REEM may be just the tool for you.
- REEM is fast. We use [Redis](https://redis.io/) (an in-memory key-value database) running [ReJSON](https://oss.redislabs.com/redisjson/) (enabling Redis to store JSON data) as a central information store.  This can support hundreds of thousands of queries per second.  We also support Pythonic access to array extension, length queries, 
- REEM is extendable.  If you want to store some complex Python object, we give users the power to control exactly how information is passed between the local program and Redis by defining custom marshallers.  REEM comes with builtin marshallers for Numpy arrays.

REEM currently offers two communication paradigms:
- get/set key-value store
- publish-subscribe

In other projects, we have used these primitives implement other paradigms, such as streams, event queues, and RPC.


## Installation

REEM is highly portable and runs on Python 3.3+.

To install the python package (and its dependencies), run
```
pip install reem
```
You will also need to have access to a Redis server with RedisJSON enabled.  See the [setup tutorial](https://reem.readthedocs.io/en/latest/gettingstarted.html) for step-by-step instructions on installing and configuring a compatible local Redis server.

## Tutorials and API documentation
See [example.py](https://www.github.com/krishauser/reem/blob/master/example.py) or the docs on [read the docs](https://reem.readthedocs.io).



## Version history

0.1.3:
- Updated to require redis-py 4.0.0+.  API is still backwards-compatible with redis-py 3.5+ (which requires rejson).
- Added `with` syntax on key-value store accessors which allows you to make many updates to an object without bogging down the Redis server. Usage is `with kvs['key'] as val: foo(val)` which is equivalent to `val=kvs['key'].read(); foo(val); kvs['key'] = val` and often much faster than `foo(kvs['key'])` if `foo` performs lots of reads and writes.
- Useless `RedisInterface.initialize()` method removed.
- Accessor `KeyValueStore.get(key)` will not fail if the top-level key exists on the Redis server but hasn't been pulled in this client.
- Added new convenience structure `TolerantKeyValueStore` which will automatically create uninitialized subkeys, throttle frequent reads, and accept both `.`-separated strings and lists of indexes as keys.

0.1.2:
- bug fixes in pub/sub implementation.
- Added `get(key,default_value)` to subkey accessor analogous to dict's `get` method.

0.1.1:
- added `get()` and `set()` to KeyValueStore for direct access to Rejson's JSON.GET / JSON.SET.

0.1.0: fork by Kris Hauser
- Can now access items by array index. 
- Much easier to work with items like normal Python objects.  Can:
    - Can treat accesssors as variables using `read()` and `write()`, e.g., `var = server['key']; var.read(); var.write(x)`. (See bug fix note below).  
    - Delete items via `del server['key']` or `del server['key']['subkey']` (uses Rejson's JSON.DEL)
    - Increment/decrement values via  `server['key']['subkey'] += 1` or `-=` (uses Rejson's JSON.NUMINCRBY).  Note: does not work for Numpy arrays.
    - Multiply/divide values via `server['key']['subkey'] *= 2` or `/=` (uses Rejson's JSON.NUMMULTBY).  Note: does not work for Numpy arrays.
    - Append to arrays via `server['key'].append(x)` or `server['key']['subkey'].append(x)` (uses Rejson's JSON.ARRAPPEND)
    - Multiple append to arrays via `server['key'] += [x,y,z]` or `server['key']['subkey'] += [x,y,z]` (uses Rejson's JSON.ARRAPPEND)
    - Get sizes of arrays/objects using `len(server['key'])` or `len(server['key']['subkey'])` (uses Rejson's JSON.OBJLEN or JSON.ARRLEN)
    - Get types of items using `server['key'].type()` or `server['key']['subkey'].type()` (uses Rejson's JSON.TYPE)
- KeyValueStore, PublishSpace, SilentSubscriber, and CallbackSubscriber are now in the global reem namespace.  Also, they can be given a string host rather than separately having to create a RedisInterface object.
- KeyValueStore and PublishSpace are now thread safe. (Note: not thoroughly tested yet).
- Objects retrieved by ['key'] no longer get clobbered when accessing ['subkey'].  E.g.,
   ```
   kvs['topkey'] = {'subkey':{'foo':3}}
   a = kvs['topkey']
   b = a['subkey']
   b['foo'] = 4
   print(a.read())  #prior version unexpected prints {'subkey':{'foo':3},'foo':4}, new version prints {'subkey'{'foo':4}} as expected.
   ```
- Slight performance improvements for deeply nested accesses
- Python 2 version automatically returns json objects with keys / values as str instead of unicode.

0.0.x: original from Trishul Nagenalli
