#!/usr/bin/env python

"""
packet
"""

import struct

class Packet:

    def __init__(self):

        # header
        self._author = 0
        self._version = 0
        self._request = 0
        self._length = 0
        self._verify = 0
        self._device = 0
        # body
        self._body = ''
        # socket
        self._conn = ''

    # setter
    def set_author(self, author):
        self._author = author
    def set_version(self, version):
        self._version = version
    def set_request(self, request):
        self._request = request
    def set_length(self, len):
        self._length = len
    def set_verify(self, verify):
        self._verify = verify
    def set_device(self, device):
        self._device = device
    def set_header(self, author, version, request, length, verify, device):
        self._author = author
        self._version = version
        self._request = request
        self._length = length
        self._verify = verify
        self._device = device

    def set_body(self, body):
        self._body = body
    def set_conn(self, conn):
        self._conn = conn

    # getter
    def get_author(self):
        return self._author
    def get_version(self):
        return self._version
    def get_request(self):
        return self._request
    def get_length(self):
        return self._length
    def get_verify(self):
        return self._verify
    def get_device(self):
        return self._device
    def get_header(self):
        return (self._author, self._version, self._request,
                    self._length, self._verify, self._device)
    def get_body(self):
        return self._body
    def get_conn(self):
        return self._conn


    def send(self):
        packet = struct.pack("6I%ds" % len(self._body),
            self._author, self._version, self._request,
            self._length, self._verify, self._device, self._body)
        self._conn.send(packet)

