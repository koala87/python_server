#!/usr/bin/env python2.7
#coding=utf-8

"""TCP Server based on tornado"""

__author__ = "Yingqi Jin (jinyingqi@luoha.com)"
__date__ = "Nov.14 2015"


from tornado.tcpserver import TCPServer
from tornado.tcpclient import TCPClient
from tornado.ioloop import IOLoop
from struct import pack, unpack
import time

from log import set_dir, debug, info, warning

from config import get_server, get_server_addr, get_all_server

# packet header
HEADER_LENGTH = 24

# business - socket
BUSINESS_MAP = {}

# notice businiss server
BOX_TYPE = 1
ERP_TYPE = 2
APP_TYPE = 3
INIT_TYPE = 4

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


def get_addr_str(addr):
    return '%s:%d' % (addr[0], addr[1])


class Connection(object):
    clients = set()
    header_length = HEADER_LENGTH 

    def __init__(self, stream, address):
        Connection.clients.add(self)
        info('new connection # %d from %s' % (len(Connection.clients), get_addr_str(address)))
        self._stream = stream
        self._address = address
        self._addr_str = get_addr_str(self._address) 

        self._type = 0 

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


    def set_type(self, val):
        self._type = val


    def read_header(self):
        self._stream.read_bytes(Connection.header_length, self.read_body)


    def read_body(self, header):
        self._header = header
        parts = unpack("6I", self._header)
        (self._author, self._version, self._request,
            self._length, self._verify, self._device) = parts
        debug('read header(%d, %d, %d, %d, %d, %d) from %s' % (
            self._author, self._version, self._request,
            self._length, self._verify, self._device,
            self._addr_str))

        self._stream.read_bytes(self._length, self.prepare_packet)
        

    def prepare_packet(self, body):
        debug('read body(%s) from %s' % (body, self._addr_str))
        self._body = body
        #extra_header = pack('3I', self._device, self._type)
        extra_header = ''
        pac = extra_header + self._header + self._body
        self.send_packet(pac)


    def send_packet(self, packet):
        debug('send packet:%s to for request:%d ...' % (packet, self._request))
        business = get_server(self._request)
        if business:
            if business in BUSINESS_MAP:
                conn = BUSINESS_MAP[business]
                conn.send(packet)
            else:
                warning('business server %s is not avalible' % business)
                pass
        else:
            warning('unsupported request: %d' % self._request)

        self.read_header()


    def on_close(self):
        self._stream.close()
        Connection.clients.remove(self)


class BoxConnection(Connection):
    box_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        self.set_type(BOX_TYPE)
        BoxConnection.box_clients.add(self)
        info('new box connection # %d from %s' % (len(BoxConnection.box_clients), get_addr_str(address)))
    
    def __del__(self):
        Connection.__del__(self)
        BoxConnection.box_clients.remove(self)
        info('box connection %s disconnected' % get_addr_str(address))


class AppConnection(Connection):
    app_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        self.set_type(APP_TYPE)
        AppConnection.app_clients.add(self)
        info('new app connection # %d from %s' % (len(AppConnection.app_clients), get_addr_str(address)))

    def __del__(self):
        Connection.__del__(self)
        AppConnection.app_clients.remove(self)
        info('app connection %s disconnected' % get_addr_str(address))


class ERPConnection(Connection):
    erp_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        self.set_type(ERP_TYPE)
        ERPConnection.erp_clients.add(self)
        info('new erp connection # %d from %s' % (len(ERPConnection.erp_clients), get_addr_str(address)))

    def __del__(self):
        Connection.__del__(self)
        ERPConnection.erp_clients.remove(self)
        info('erp connection %s disconnected' % get_addr_str(address))


class InitConnection(Connection):
    init_clients = set()
    def __init__(self, stream, address):
        Connection.__init__(self, stream, address)
        self.set_type(INIT_TYPE)
        InitConnection.init_clients.add(self)
        info('new init connection # %d from %s' % (len(InitConnection.init_clients), get_addr_str(address)))

    def __del__(self):
        Connection.__del__(self)
        InitConnection.init_clients.remove(self)
        info('init connection %s disconnected' % get_addr_str(address))


class KTVServer(TCPServer):
    def handle_stream(self, stream, address):
        ip, port = stream.socket.getsockname()
        port_conn_map = {
            BOX_PORT : BoxConnection,
            APP_PORT : AppConnection,
            ERP_PORT : ERPConnection,
            INIT_PORT : InitConnection,
        }
        port_conn_map[port](stream, address)


if __name__ == '__main__':
    
    set_dir('server') # set log path

    # listen BOX_PORT, APP_PORT, ERP_PORT, INIT_PORT
    info('start server ...')
    server = KTVServer()

    for port in LISTEN_PORT.values():
        server.bind(port)
        info('listen port %d ...' % port)
    server.start(0)

    IOLoop.current().start()
