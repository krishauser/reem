from __future__ import print_function

from threading import Thread, Lock
import rejson
from .utilities import *

_ROOT_VALUE_READ_NAME = "{}ROOT{}".format(ROOT_VALUE_SEQUENCE, ROOT_VALUE_SEQUENCE)

class MetadataListener:
    def __init__(self, interface):
        self.client = rejson.Client(host=interface.hostname)
        self.pubsub = self.client.pubsub()
        self.pubsub.psubscribe(['__keyspace@0__:*'])
        self.listeners = {}

    def add_listener(self, key_name, reader):
        listen_name = "__keyspace@0__:{}".format(key_name)
        self.listeners.setdefault(listen_name,[]).append(reader)

    def flush(self):
        while True:
            item = self.pubsub.get_message()
            if item is None:
                break
            channel = item['channel'].decode("utf_8")
            try:
                for listener in self.listeners[channel]:
                    listener.pull_metadata = True
            except KeyError:
                pass


class PathHandler:
    def __init__(self, writer, reader, initial_path):
        self.writer = writer
        self.reader = reader
        self.path = initial_path

    def __getitem__(self, item):
        assert check_valid_key_name(item)
        self.path = append_to_path(self.path, item)
        return self

    def __setitem__(self, instance, value):
        assert check_valid_key_name(instance)
        self.path = append_to_path(self.path, instance)
        self.writer.send_to_redis(self.path, value)


class ReadablePathHandler(PathHandler):
    def read(self):
        server_value = self.reader.read_from_redis(self.path)
        if type(server_value)==dict and _ROOT_VALUE_READ_NAME in server_value:
            return server_value[_ROOT_VALUE_READ_NAME]
        return server_value


class ActiveSubscriberPathHandler(PathHandler):
    def read(self):
        return_val = self.reader.local_copy
        dissect_path = self.path[1:]
        if len(dissect_path) == 0:
            pass
        else:
            for key in dissect_path.split("."):
                return_val = return_val[key]
        if type(return_val) == dict:
            return copy_dictionary_without_paths(return_val, [])
        return return_val

    def __setitem__(self, instance, value):
        raise Exception("Cannot set value for a subscriber")


class ChannelListener(Thread):
    def __init__(self, interface, channel_name, callback_function, kwargs):
        Thread.__init__(self)
        self.client = rejson.Client(host=interface.hostname)
        self.pubsub = self.client.pubsub()
        self.pubsub.psubscribe([channel_name])
        self.callback_function = callback_function
        self.kwargs = kwargs
        self.first_item_seen = False

    def run(self):
        for item in self.pubsub.listen():
            # First Item is a generic message that we need to get rid of
            if not self.first_item_seen:
                self.first_item_seen = True
                continue
            channel = item['channel'].decode("utf_8")
            message = item['data']
            self.callback_function(channel=channel, message=message, **self.kwargs)

"""
Naming:
Rapid Extendable Middleware
Redis Medium Extendable Middleware
Redis Robotic Communication

Redis Extendable Middleware

Extendable Efficient Redis Middleware
Redis Extendable Efficient Middleware
reem
"""
