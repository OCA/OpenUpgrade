import BaseHTTPServer
import DAV
import os

from xml.dom import ext

from dav_auth import tinyerp_auth
from dav_fs import tinyerp_handler

import threading
import pooler

#db_name = 'terp'
db_name = ''
host='localhost' #  give  IP address like '192.168.0.41'  for remotly access
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
	ds = dav_server(host, port)
	ds.start()
except Exception , e:
	print e


##
## I try to run multiple webdav server fetch from different repository from different dbs , but do not suceess
##
#cr=False
#db_service = netsvc.LocalService("db")
#db_list=db_service.list()
#web_servers=[]
#
#for db_name in db_list:
#	try:
#		db = pooler.get_db_only(db_name)
#		cr = db.cursor()
#		cr.execute("select rep.directory_id,rep.server_url,rep.server_port from document_repository as rep where rep.active",(db_name,))
#		res=cr.fetchall()
#		if res:
#			for (directory_id,host,port) in res:
#				if (host,port) not in web_servers:
#					web_servers.append((host,port))
#					try:
#						ds = dav_server(host, port)
#						ds.start()
#					except Exception , e:
#						print e
#		cr.close()
#	except Exception , e:
#		print db_name


