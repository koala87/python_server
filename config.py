#!/usr/bin/env python2.7
#coding=utf-8
#!/usr/bin/env python2.7
#coding=utf-8

"""read config"""
__author__ = "Yingqi Jin (jinyingqi@luoha.com)"

import os
import ConfigParser
from singleton import Singleton

class Configure(Singleton):

    def __init__(self):
        self.server_addr_map = {}
        self.request_server_map = {}
        self.request_function_map = {}
        self.read_config()

    def read_config(self, fname='route.conf'):
        if not os.path.exists(fname):
            return
        cf = ConfigParser.ConfigParser()
        cf.read(fname)
        secs = cf.sections()
        
        if 'server' in secs:
            opts = cf.options('server')
            for opt in opts:
                str_val = cf.get('server', opt)
                self.server_addr_map[opt] = str_val

        for sev in self.server_addr_map.iterkeys():
            if sev in secs:
                opts = cf.options(sev)
                for opt in opts:
                    str_val = cf.get(sev, opt)
                    request = int(opt)
                    self.request_function_map[request] = str_val
                    self.request_server_map[request] = sev

    def get_all_server(self):
        return self.server_addr_map

    def get_server(self, request):
        return self.request_server_map.get(request, None)

    def get_server_addr(self, server):
        return self.server_addr_map.get(server, None)

    def dump(self):
        print self.server_addr_map
        print self.request_server_map


__configure = Configure()

def get_all_server():
    return __configure.get_all_server()

def get_server(request):
    return __configure.get_server(request)

def get_server_addr(server):
    return __configure.get_server_addr(server)

def dump_config(server):
    return __configure.dump();

def read_config(fname):
    __configure.read_config(fname)


if __name__ == '__main__':

    print get_server(10001)
    #print get_server(25000)
    print get_server_addr('control')
    #print get_server_addr('game')
    print get_all_server()
