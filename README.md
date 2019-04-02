# REEM

REEM is a centralized middleware package for robotic communication that utilizes Redis, a fast in-memory key-value database. It is designed for ease of use and efficiency.

## Design Philosophy:
REEM expects you will store your data as a nested data structure - think of communication between computers as passing JSON's between machines. REEM is built to model as much data as it can using Redis's [ReJSON](https://pypi.org/project/rejson/) module. This works great for serializable data, but we often want to work with non-serializable types like numpy arrays. Users can define encoder/decoder objects called Ships that define how non-serializable types should be pushed to and retrieved from Redis. REEM provides a default Ship for handling numpy arrays.

## Tutorial

This tutorial will demonstrate how to set up a Redis/ReJSON database on your local computer and connect to it using REEM.

Requirements:
- Python 3
- Linux/macOS (ReJSON requirement, though you can run ReJSON with Docker on Windows)


Open a new terminal and navigate to the directory you would like to work in. **We will refer to this directory as ``.``**

### Redis
First we will install Redis. If at any point, you are stuck in this tutorial, take a look at the [Redis Quickstart](https://redis.io/topics/quickstart) page for help.

Run the following commands in your terminal
```bash
mkdir database-server
cd database-server
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
```
Congratulations! You have installed Redis. Test your installation by running the following in your terminal
```bash
redis-server --daemonize yes
redis-cli
```
You just started a redis server and entered the command line interface (cli) to access the server. Your prompt will look a little different now. To test if the connection is working, type in ``ping`` and you shold see that the redis server you began responds ``PONG``. Then shutdown the server by issuing the ``shutdown`` command and exit the redis-cli with ``ctrl-c``. This whole exchange should look like this:

```bash
MacBook-Pro:redis-stable trishul$ redis-server --daemonize yes
85795:C 28 Mar 2019 14:26:28.140 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
85795:C 28 Mar 2019 14:26:28.140 # Redis version=5.0.3, bits=64, commit=00000000, modified=0, pid=85795, just started
85795:C 28 Mar 2019 14:26:28.140 # Configuration loaded
MacBook-Pro:redis-stable trishul$ redis-cli
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> shutdown
not connected>
MacBook-Pro:redis-stable trishul$
```
[//]: ![](https://i.imgur.com/OyL42kS.png)


[//]: #![](https://i.imgur.com/448WsNT.png)

### ReJSON
Now we will install ReJSON. Refer to [ReJSON's Instructions](https://oss.redislabs.com/redisjson/) for additional help if necessary.
```bash
cd ..
git clone https://github.com/RedisLabsModules/redisjson.git
cd rejson
make
cd ..
```
ReJSON is now installed on your computer as an so file inside ``.rejson/src/rejson.so``. We need to tell Redis to use this module. We will do this with a redis configuration file. Download [this example file](https://github.com/tn74/reem/blob/master/examples/redis.conf) configuration file and put it inside the ``database-server`` directory. Then run the following
```bash
redis-server redis.conf --daemonize yes
redis-cli
```
You should see your prompt change again. Enter ``JSON.SET foo . 0`` and verify the output looks as below
```
127.0.0.1:6379> JSON.SET foo . 0
OK
```
You now have a server running Redis and ReJSON!

### Running REEM
Exit the redis-cli by entering ``ctrl-C``. In your terminal, install REEM and all of its dependencies with the following command:
```bash
pip3 install reem rejson redis six numpy
```

Let's try running something!

Copy the following code into a file ``example.py`` into the directory ``.``
```python
from reem.connections import RedisInterface
from reem.datatypes import KeyValueStore
import numpy as np

interface = RedisInterface(host="localhost")
interface.initialize()
server = KeyValueStore(interface)

# Set a key and read it and its subkeys
server["foo"] = {"number": 100.0, "string": "REEM"}
print("Reading Root  : {}".format(server["foo"].read()))
print("Reading Subkey: {}".format(server["foo"]["number"].read()))

# Set a new key that didn't exist before to a numpy array
server["foo"]["numpy"] = np.random.rand(3,4)
print("Reading Root  : {}".format(server["foo"].read()))
print("Reading Subkey: {}".format(server["foo"]["numpy"].read()))

```
In ``.``, run ``python3 example.py``
If it runs without error, congratulations! Installation was successful. Let's look deeper at the code.

### Initialization
```python
interface = RedisInterface(host="localhost")
interface.initialize()
server = KeyValueStore(interface)
```
The ``interface`` variable defines what a connection to redis is going to look like. You will need to specify the host name of the redis server you wish to connect to.

Every datatype you wish to instantiate later is going to refer to this interface to know what server it is connected to. Here, we instantiate a ``KeyValueStore `` object with the interface as the variable ``server``. A ``KeyValueStore`` object serves as your standard get and set database.


### Database Syntax
```python
# Set a key and read it and its subkeys
server["foo"] = {"number": 100.0, "string": "REEM"}
print("Reading Root  : {}".format(server["foo"].read()))
print("Reading Subkey: {}".format(server["foo"]["number"].read()))

# Set a new key that didn't exist before to a numpy array
server["foo"]["numpy"] = np.random.rand(3,4)
print("Reading Root  : {}".format(server["foo"].read()))
print("Reading Subkey: {}".format(server["foo"]["numpy"].read()))
```
In the first section of this example code, we set a top level json inside the server to be a python dictionary. Next we read exactly what we wrote. What we get back is a python dictionary identical to the one we submitted. We can also execute a read on a specific subkey of the data we set as we do in third line.

In the second section of the code, we set a numpy array inside the redis server. Normally, numpy arrays can't be stored in JSONs because they are not serialzable. Internally, REEM handles it differently, but you don't have to worry about that. If you are interestined in handling more non-serializable data types, see the ``Ship`` class documentation, coming soon.

Congratulations! You have completed the basic tutorial on REEM. You can explore further topics of interest to you:
- Key Value Store Paradigm
- Publish/Subscribe Paradigm
<!-- #### A Publish/Subscribe Example
Following a successful installation, you should be able to run any of the examples listed in this repository!

Download [ImageProcessing.py](https://github.com/tn74/reem/blob/master/examples/ImageProcessing.py) into your working directory (the one that contains database-server). Execute the following:
```bash
cd ..
python3 ImageProcessing.py
```
If the file executes without error, you have successfully installed and ran a program with REEM!  -->
## Datatypes
The following sections assume you are running a local redis server with rejson. See the [tutorial](#Tutorial) to get those up and running.

## KeyValueStore Database

The ``KeyValueStore`` object is a get and set database with nested data structures. The interface to the user is almost identical to that of a python dictionary. Each time you set something in the "dictionary", the corresponding entry is updated in the server. To read from the server, you access the entry in the "dictionary" and call ``.read()``

#### Set Up
```python
from reem.datatypes import KeyValueStore
from reem.connection import RedisInterface

interface = RedisInterface(host="localhost")
interface.initialize()
server = KeyValueStore(interface)
```
The above is all you need to start your connection to the database. See the [initialization](#Initialization) section of the tutorial for more information about the interface variable.


#### Basic Usage
```python
data = {'number': 1000, 'string': 'REEM'}
server["foo"] = flat_data

bar = server["foo"].read()
# Sets bar = {'number': 1000, 'string': 'REEM'}

bar = server["foo"]["number"].read()
# Sets bar = 1000
```
The first section writes a dictionary to the Redis Server. The second section demonstrates that you can read either the whole dictionary or a subkey of it. The result will be identical to what you would get if you treated server like a local dictionary.

#### Updates
You can update and read entries as you would a normal python dictionary:

```python
server["foo"]["new_key"] = data

bar = server["flat_data"].read()
# bar = {'number': 1000, 'string': 'REEM', 'new_key':{'number': 1000, 'string': 'REEM'} }

bar = server["flat_data"]["new_key"]["number"].read()
# bar = 1000

import numpy as np
server["foo"] = np.arange(3)

bar = server["foo"].read()
# bar = array([0, 1, 2])
```

#### Limitations

1. Cannot use non-string Keys
```python
server["foo"] = {0:"zero", 1:"one"} # Not Okay
server["foo"] = {"0":"zero", "1":"one"} # Okay
```
REEM currently assumes all keys are strings to avoid having to parse JSON keys to determine if they are strings or numbers.

2. Cannot have a list with nonserializable types.
```python
server["foo"] = {"bar":[np.arange(3), np.arange(4)]} # Not Okay
server["foo"] = {"bar":[3, 4]} # Okay
```
REEM does not presently check lists for non serializable types. We hope to allow this in a future release. For now, we ask you substitute the list with a dictionary
```python
server["foo"] = {"bar":[np.arange(3), np.arange(4)]} # Not Okay
server["foo"] = {"bar":{"arr1": np.arange(3), "arr2": np.arange(4)}} # Okay
```

## Publish Subscribe
The Publish-Subscribe Paradigm in REEM is designed to be as user-friendly as possible. Users publish data the same way they would set an item in a dictionary. Users subscribe to data by specifying what path inside that nested dictionary they would like to listen to.

### Publishing
Publishing is implemented with a PublishSpace Object. It is initialized with a RedisInterface object as below:

```python
from reem.datatypes import PublishSpace
from reem.connection import RedisInterface

interface = RedisInterface(host="localhost")
interface.initialize()
publisher = PublishSpace(interface)
```
Treat ``publisher`` like a dictionary. Each time you set something in ``publisher``, the corresponding entry in the server is updated and a message is published stating that path was updated. Subscribers will see the message and pull the updated data. The below code gives an example

```python
data = {"image": np.random.rand(640, 480, 3), "id": 0}

# publishes raw_image
publisher["raw_image"] = data

# publishes raw_image.id
publisher["raw_image"]["id"] = 1
```
The ``PublishSpace`` object is implemeted exactly as a ``KeyValueStore`` object with two differences:
1. Updated paths are published
2. Cannot read from a ``PublishSpace`` object.


### Subscribing
Subscribes listen to a key on the Redis Server and will act based on changes to that key OR its subkeys. For example a subscriber to the key "camera_data" will be notified if "camera_data" is freshly uploaded by a publisher or if the path "camera_data.image" is updated.

Subscribing is implented in two different ways - ``SilentSubscriber`` and ``CallbackSubscriber``. The former is designed to feel like a local variable that tracks the data in the server as closely as possible. It silently updates every time something is published. The latter allows the user to specify a function that should be called every time a message is published.

#### SilentSubscriber

A silent subscriber is initialized by specifying a channel name and an interface as below. Be sure to call subscriber.listen()! It engages the subscriber. Without it, the subcriber will not be tracking published updates

```python
from reem.datatypes import PublishSpace, SilentSubscriber
from reem.connection import RedisInterface

interface = RedisInterface(host="localhost")
interface.initialize()

# Initialize a publisher
publisher = PublishSpace(interface)

# Initialize a silent subscriber
subscriber = SilentSubscriber(channel="silent_channel", interface=interface)
subscriber.listen()
```

To read the subscribers data, access it as though it were a dictionary. If you need to access the whole data strucutre associated with this channel, call ``subscriber.value()``
```python
publisher["silent_channel"] = {"number": 5, "string":"REEM"}
time.sleep(0.01)

foo = subscriber["number"].read()
# foo = 5
foo = subscriber.value()
# foo = {"number": 5, "string":"REEM"}


publisher["silent_channel"] = 5
time.sleep(0.01)

foo = subscriber.value()
# foo = 5
```

#### CallbackSubscriber

A callback subscriber allows you to call a function after every update. The function you set is required to take in keyword arguments ``data`` and ``updated_path`` that give information about the update. The behavior of the callback subscriber is as follows:
1. Listen to channel
2. Hear ``updated_path`` was modified in the server
3. Pull new data at ``updated_path``
4. Insert new data into local copy
5. Call user function with arguments
    - ``data`` - all data underneath this channel name in the server
        - Includes what was updated and what was there before
    - ``updated_path`` - the path that was modified by the recent publish
    - ``**kwargs`` - unpacked keyword arguments that user provided with instantiation of subscriber.

The initialization of a ``CallbackSubscriber`` is as below:
```python
from reem.datatypes import PublishSpace, CallbackSubscriber
from reem.connection import RedisInterface

interface = RedisInterface(host="localhost")
interface.initialize()

# Initialize a publisher
publisher = PublishSpace(interface)


# Callback Function
def callback(data, updated_path, foo):
    print("Foo = {}".format(foo))
    print("Data = {}".format(data))

# # Initialize a callback subscriber
subscriber = CallbackSubscriber(channel="callback_channel",
                                interface=interface,
                                callback_function=callback,
                                kwargs={"foo":5})
subscriber.listen()
```
The execution of the callback function happens in a secondary thread. When the following commands are executed by the publisher, the subscriber will automatically listen and act.

```python
publisher["callback_channel"] = {"number": 5, "string": "REEM"}
publisher["callback_channel"]["number"] = 6
```
The standard out of the above execution is
```
Foo = 5
Updated Path = callback_channel
Data = {'number': 6, 'string': 'REEM'}
Foo = 5
Updated Path = callback_channel.number
Data = {'number': 6, 'string': 'REEM'}
```