import BaseHTTPServer
import DAV
import os

from xml.dom import ext

from dav_auth import tinyerp_auth
from dav_fs import tinyerp_handler

import threading
import pooler

db_name = ''
host=''
port=8008

class dav_server(threading.Thread):
	def __init__(self, host, port, db_name=False, directory_id=False):
		super(dav_server,self).__init__()
		self.host = host
		self.port = port
		self.db_name = db_name
		self.directory_id = directory_id

	def run(self):
		server = BaseHTTPServer.HTTPServer
		handler = tinyerp_auth
		handler.db_name = db_name
		handler.IFACE_CLASS  = tinyerp_handler( self.host,self.port,  True )
		handler.verbose = True
		try:
			runner = server( (self.host, self.port), handler )
			runner.serve_forever()
		except Exception, e:
			print e,self.host,self.port

try:
	print 'Starting Server', host, port
	ds = dav_server(host, port)
	ds.start()
except Exception , e:
	print e

