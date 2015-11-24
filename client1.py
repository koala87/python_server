#!/usr/bin/env python
#!coding=utf-8

import sys
import socket
import threading
import struct
import time 
import random

import packet

def get_message():
    #msg = ['hello', 'world', 'sally', 'harry', 'jack', 'tt', 'money', 'bbq']
    msg = ['hello world']
    return msg[random.randint(0, len(msg)-1)] 
    

class Client(threading.Thread):

    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._address = (ip, port)
        self.thread_stop = False

    def run(self):
        self._sock.connect(self._address)
        print self

        while not self.thread_stop:
            pac = packet.Packet()
            msg = get_message()
            pac.set_header(17, 100, 10001, len(msg), 65536, 101)
            pac.set_body(msg)
            pac.set_conn(self._sock)
            pac.send()

            buf = self._sock.recv(1024)
            header = buf[0:24]
            author, version, request, length, verify, device = struct.unpack("6I", header)
            body = buf[24:]
            print 'receive header:(%d, %d, %d, %d, %d, %d)' % (author, version, request, length, verify, device)
            print 'receive body: %d %s' % (len(body), body)
            

            time.sleep(1)

    def stop(self):
        self.thread_stop = True


if __name__ == '__main__':

    num = 10
    port = 58849

    if len(sys.argv) >= 2:
        try:
            num = int(sys.argv[1])
        except:
            pass

    threads = []
    for i in range(num):
        #threads.append(Client('localhost', port))
        threads.append(Client('192.168.1.233', 2825))
    
    for i in threads: 
        i.start()
    
    #for i in threads:
    #    i.stop()
