# -*- coding: utf-8 -*-

from xmlrpclib import ServerProxy

url = 'http://127.0.0.1:8000/soupport/api/ws/xmlrpc'

server = ServerProxy(url)
data = server.activation('123', '1400025500-9')
#data = server.signature()

print data
