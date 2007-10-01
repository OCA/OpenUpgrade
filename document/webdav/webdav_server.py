import BaseHTTPServer
import DAV
import os

from xml.dom import ext

from dav_auth import tinyerp_auth
from dav_fs import tinyerp_handler

import threading
import pooler

db_name = 'terp'

class dav_server(threading.Thread):
	def __init__(self, host, port, db_name, directory_id):
		super(dav_server,self).__init__()
		self.host = host
		self.port = port
		self.db_name = db_name
		self.directory_id = directory_id

	def run(self):
		server = BaseHTTPServer.HTTPServer
		handler = tinyerp_auth
		handler.db_name = db_name
		handler.IFACE_CLASS = tinyerp_handler(db_name, 'http://%s:%s/' % (host, port), self.directory_id, True )
		handler.verbose = True
		runner = server( (host, port), handler )
		runner.serve_forever()

cr=False
try:
	db = pooler.get_db_only(db_name)
	cr = db.cursor()
except:
	db=None
if cr:
	try:
		cr.execute("select server_url,server_port,directory_id from document_repository where active")
		for host,port,directory_id in cr.fetchall():
			ds = dav_server(host, port, db_name, directory_id)
			ds.start()
		cr.close()
	except:
		pass
