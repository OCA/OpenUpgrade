import BaseHTTPServer
import DAV
import os

from xml.dom import ext

import netsvc
from dav_auth import tinyerp_auth
from dav_fs import tinyerp_handler
from tools.config import config

from tools.misc import ustr,exception_to_unicode
import threading
import pooler

class dav_server(threading.Thread):
	def __init__(self):
		super(dav_server,self).__init__()
		self.host = config.get_misc('webdav','host','')
		self.port = int(config.get_misc('webdav','port',8008))
		self.db_name = config.get_misc('webdav','db_name','')
		self.directory_id = config.get_misc('webdav','directory_id',False)

	def log(self,level,msg):
		""" An independent log() that will release the logger upon return
		"""
		logger = netsvc.Logger()
		logger.notifyChannel('webdav', level, msg)
		
	def run(self):
		server = BaseHTTPServer.HTTPServer
		handler = tinyerp_auth
		handler.db_name = self.db_name
		handler.IFACE_CLASS  = tinyerp_handler( self.host,self.port,  True )
		handler.verbose = config.get_misc('webdav','verbose',True)
		handler.debug = config.get_misc('webdav','debug',True)
		try:
			self.log(netsvc.LOG_INFO,"Starting WebDAV service at %s:%d" % (self.host,self.port))
			runner = server( (self.host, self.port), handler )
			runner.serve_forever()
		except Exception, e:
			raise

try:
	if (config.get_misc('webdav','enable',False)):
		ds = dav_server()
		ds.start()
except Exception, e:
	logger = netsvc.Logger()
	logger.notifyChannel('webdav', netsvc.LOG_ERROR, 'Cannot launch webdav: %s' % exception_to_unicode(e))

