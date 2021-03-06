from __future__ import print_function

import rejson
from .supports import  MetadataListener
from .ships import *
from threading import Lock


class RedisInterface:
    """

    """
    def __init__(self, host='localhost', ships=[NumpyShip()]):
        self.hostname = host
        self.ships = ships
        self.client = rejson.Client(host=host, decode_responses=True)
        self.client_no_decode = rejson.Client(host=host)
        self.metadata_listener = MetadataListener(self)
        self.INTERFACE_LOCK = Lock()

        self.label_to_shipper = {}
        for sh in self.ships:
            self.label_to_shipper[sh.get_label()] = sh

        self.shipper_labels = [sh.get_label() for sh in ships]

    def initialize(self):
        """
        Call before doing anything with this connection
        :return:
        """
        pass