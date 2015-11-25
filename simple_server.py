#!/usr/bin/env python2.7
#coding=utf-8

"""KTV Server based on tornado"""

__author__ = "Yingqi Jin (jinyingqi@luoha.com)"

import sys
import time
import logging
from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop
from struct import pack, unpack


# packet header : 24 bytes (author, version, request, verify, length, device)
HEADER_LENGTH = 24

# listen port
BOX_PORT = 58849
ERP_PORT = 25377
APP_PORT = 3050
INIT_PORT = 11235

LISTEN_PORT = {
    'box' : BOX_PORT,
    'erp' : ERP_PORT,
    'app' : APP_PORT,
    'ini' : INIT_PORT,
    }


def init_log():
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s - %(process)-6d - %(threadName)-10s - %(levelname)-8s]\t%(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='simple_server.log',
        filemode='w')
    
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    sh.setFormatter(formatter)
    logging.getLogger('').addHandler(sh)


def get_addr_str(addr):
    return '%s:%d' % (addr[0], addr[1])


class Connection(object):
    clients = set()
    header_length = HEADER_LENGTH 

    def __init__(self, stream, address):
        Connection.clients.add(self)
        self._stream = stream
        self._address = address
        self._addr_str = get_addr_str(self._address) 

        self._header = ''
        self._body = ''
        self._author = ''
        self._version = ''
        self._request = 0
        self._length = 0
        self._verify = 0
        self._device = 0

        self._stream.set_close_callback(self.on_close)
        self.read_header()


    def read_header(self):
        self._stream.read_bytes(Connection.header_length, self.read_body)


    def read_body(self, header):
        self._header = header
        parts = unpack("6I", self._header)
        from socket import ntohl
        parts = [ntohl(x) for x in parts]

        (self._author, self._version, self._request,
            self._verify, self._length, self._device) = parts
        logging.debug('read header(%d, %d, %d, %d, %d, %d) from %s' % (
            self._author, self._version, self._request,
            self._verify, self._length, self._device,
            self._addr_str))

        self._stream.read_bytes(self._length, self.parse_main)


    def parse_main(self, body):
        logging.debug('read body(%s) from %s' % (body, self._addr_str))
        self._body = body

    def on_close(self):
        self._stream.close()
        Connection.clients.remove(self)
        logging.info('remote client %s' % self.getName())


class BoxConnection(Connection):
    box_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        BoxConnection.box_clients.add(self)
        self._stream.set_close_callback(self.on_close)
        logging.info('new box connection # %d from %s' % (len(BoxConnection.box_clients), get_addr_str(address)))
    
    def on_close(self):
        Connection.on_close(self)
        BoxConnection.box_clients.remove(self)
        logging.info('box connection %s disconnected' % get_addr_str(self._address))


class AppConnection(Connection):
    app_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        AppConnection.app_clients.add(self)
        self._stream.set_close_callback(self.on_close)
        logging.info('new app connection # %d from %s' % (len(AppConnection.app_clients), get_addr_str(address)))

    def on_close(self):
        Connection.on_close(self)
        AppConnection.app_clients.remove(self)
        logging.info('app connection %s disconnected' % get_addr_str(self._address))


class ERPConnection(Connection):
    erp_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        ERPConnection.erp_clients.add(self)
        self._stream.set_close_callback(self.on_close)
        logging.info('new erp connection # %d from %s' % (len(ERPConnection.erp_clients), get_addr_str(address)))

    def on_close(self):
        Connection.on_close(self)
        ERPConnection.erp_clients.remove(self)
        logging.info('erp connection %s disconnected' % get_addr_str(self._address))


class InitConnection(Connection):
    init_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        InitConnection.init_clients.add(self)
        self._stream.set_close_callback(self.on_close)
        logging.info('new init connection # %d from %s' % (len(InitConnection.init_clients), get_addr_str(address)))

    def on_close(self):
        Connection.on_close(self)
        InitConnection.init_clients.remove(self)
        logging.info('init connection %s disconnected' % get_addr_str(self._address))


# handle_stream will be called once new connection is created
class KTVServer(TCPServer):
    def handle_stream(self, stream, address):
        ip, port = stream.socket.getsockname()
        port_conn_map = {
            BOX_PORT : BoxConnection,
            APP_PORT : AppConnection,
            ERP_PORT : ERPConnection,
            INIT_PORT : InitConnection,
        }
        # instance new connection based on port type
        port_conn_map[port](stream, address)


if __name__ == '__main__':
    
    init_log()

    host = 'localhost'

    logging.info('start server ...')
    server = KTVServer()

    for port in LISTEN_PORT.values():
        server.bind(port, host)
        logging.info('listen %s port %d ...' % (host, port))

    # here we fire one process because there're no processs safe vars
    server.start(1)

    IOLoop.current().start()
