#!/usr/bin/python
#coding: utf-8

from  hashlib import sha1
import random

from urllib import urlencode
import httplib2
import sys

#from config import *
app_key=""
app_secret=""
uid=""
realm = "xiaoi.com"
method = "POST"
uri = "/robot/ask.do"
chars = "abcdefghijklmnopqrstuvwxyz0123456789"

def genkey():
    nonce = ''
    for j in range(0,40):
        nonce +=random.choice(chars)
    HA1 = sha1( ":".join([app_key, realm, app_secret]) ).hexdigest()
    HA2 = sha1( ":".join([method, uri]) ).hexdigest()
    sign = sha1( ":".join([HA1, nonce, HA2]) ).hexdigest()
    auth ='app_key="%s", nonce="%s", signature="%s"' %(app_key, nonce, sign)
    return auth

auth = genkey()
print auth
httpheader = {
    'X-Auth': auth
}

data={'question':sys.argv[1], 'userId':uid, 'type':0, 'platform':'fuck'}

url='http://nlp.xiaoi.com/robot/ask.do'
h = httplib2.Http()
res, cont = h.request(url, method='POST', headers=httpheader, body=urlencode(data))
print cont
