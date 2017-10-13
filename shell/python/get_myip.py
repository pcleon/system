#!/usr/bin/env python
#coding:utf8

import socket

get_myip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        (addr, port) = s.getsockname()
        s.close()
        return addr
    except socket.error, e:
        print e
