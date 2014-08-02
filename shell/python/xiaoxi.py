#!/usr/bin/python
#coding: utf-8

from  hashlib import sha1
import random

from urllib import urlencode
import urllib2
import sys

#from config import *
app_key="HvYMQc7fGyyf"
app_secret="Bx6GJ8E3fzD5Xde1wQgY"
uid="api-wplnnzvb"

realm = "xiaoi.com"
method = "POST"
uri = "/robot/ask.do"
chars = "abcdefghijklmnopqrstuvwxyz0123456789"

def genkey():
    nonce = ''
    for j in range(40):
        nonce +=random.choice(chars)
    HA1 = sha1( ":".join([app_key, realm, app_secret]) ).hexdigest()
    HA2 = sha1( ":".join([method, uri]) ).hexdigest()
    sign = sha1( ":".join([HA1, nonce, HA2]) ).hexdigest()
    auth ='app_key="%s",nonce="%s",signature="%s"' %(app_key, nonce, sign)
    return auth

def req(content='你好'):
    auth = genkey()
    #print auth
    httpheader = { 'X-Auth': auth }
    data = {
            'question':content,
            'userId':uid,
            'type':0,
            'platform':'weixin'
            }
    url='http://nlp.xiaoi.com%s?platform=%s' % (uri, data['platform'])
    request = urllib2.Request(url, urlencode(data), httpheader)
    res = urllib2.urlopen(request, timeout=2)
    return res.read()



if __name__ == "__main__":
    try :
        ask = sys.argv[1]
        print req(ask)
    except IndexError:
        print req()
