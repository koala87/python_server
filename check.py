#!/usr/bin/env python
#!coding=utf-8

"""check KTVServer connections"""

__author__ = "jinyingqi <jingyingqi@luoha.com>"

import sys
import time
import json
import socket
import struct
import logging
from optparse import OptionParser


def init_log():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='check.log',
        filemode='w')
    
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    sh.setFormatter(formatter)
    logging.getLogger('').addHandler(sh)


def register_options():
    parser = OptionParser()
    parser.add_option("--host", dest="host",
        default="192.168.1.233", help="specify host")
    parser.add_option("-p", "--port", dest="port",
        type="int",
        default=3050, help="specify port")
    parser.add_option("-m", "--max", dest="max",
        type="int",
        default=2, help="max wait time")
    parser.add_option("-v", "--verbose", dest="verbose",
        action="store_true",
        default=False, help="dump verbose")
 
    (options, args) = parser.parse_args() 
    return options


def verify_data(data):
    """verify server return data"""
    if len(data) < 24:
        logging.error('received data length less than 24')

    parts = struct.unpack("6I", data[0:24]) 
    parts = [str(socket.ntohl(x)) for x in parts]
    header = ', '.join(parts)

    body = ''
    try:
        body = json.loads(data[24:])
    except:
        logging.error('received data body is not JSON string')
        return ''

    logging.debug('header:%s body:%s' % (header, json.dumps(body, indent=4)))

    try:
        if 'app_connections' in body and body['app_connections']:
            num = len(json.loads(body['app_connections']))
            logging.info('app connections: %d' % num) 

        if 'box_connections' in body and body['box_connections']:
            num = len(json.loads(body['box_connections']))
            logging.info('box connections: %d' % num)

        if 'erp_connections' in body and body['erp_connections']:
            num = len(json.loads(body['erp_connections']))
            logging.info('erp connections: %d' % num)

        if 'box' in body and body['box']:
            num = len(json.loads(body['box']))
            logging.info('box check: %d' % num)

        if 'databases' in body and body['databases']:
            logging.info('db: %s' % body['databases']['db_status'])
    except:
        logging.error('data in body is not JSON string')


if __name__ == '__main__':

    init_log()

    opts = register_options()
    host = opts.host
    port = opts.port

    logging.info('start check ... server %s:%d' % (host, port))

    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = (host, port)
    try:
        sock.connect(addr)
        name = sock.getsockname()
        logging.info('%s:%d' % (name[0], name[1]))
    except:
        logging.warning('can not connect to %s:%d' % (host, port)) 
        sys.exit(1)

    # send check request
    body = 'hi ~'
    elems = [socket.htonl(x) for x in [17, 100, 10018, 65536, len(body), 520] ]

    header = struct.pack('6I', elems[0], elems[1],
        elems[2], elems[3], elems[4], elems[5])
    msg = header + body
    try:
        sock.send(msg)
        logging.debug('send msg(%d:%s) to %s:%d' % (len(msg), msg, host, port))
    except:
        logging.warning('can not send msg(%d:%s) to %s:%d' 
            % (len(msg), msg, host, port))
        sys.exit(1)

    # read check data and verify
    start = time.time()
    sock.setblocking(0)
    recv = ''
    while True:
        time.sleep(0.1) 
        try:
            recv = sock.recv(4096)
        except:
            pass
        if recv or time.time() - start > opts.max:
            break

    # verify data and return report
    verify_data(recv)

    logging.info('done')
