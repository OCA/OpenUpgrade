from DAV.WebDAVServer import DAVRequestHandler
from DAV.BufferingHTTPServer import BufferedHTTPRequestHandler
from DAV.AuthServer import AuthRequestHandler,BufferedAuthRequestHandler
import sys
import pooler
from service import security
import os
import string

auth={'user':'root','pwd':''}
class tinyerp_AuthRequestHandler(AuthRequestHandler):
	def handle(self):
		"""
		Special handle method with buffering and authentication
		"""
		self.infp=os.tmpfile()
		self.infp.write("------------------------------------------------------------------------------\n")
		self.raw_requestline = self.rfile.readline()
		self.infp.write(self.raw_requestline)
		self.request_version = version = "HTTP/0.9" # Default
		requestline = self.raw_requestline

		self.command = requestline
		if requestline[-2:] == '\r\n':
			requestline = requestline[:-2]
		elif requestline[-1:] == '\n':
			requestline = requestline[:-1]

		self.requestline = requestline
		words = string.split(requestline)
		if len(words) == 3:
			[command, path, version] = words
			if version[:5] != 'HTTP/':
				self.send_error(400, "Bad request version (%s)" % `version`)
				return
		elif len(words) == 2:
			[command, path] = words
			if command != 'GET':
				self.send_error(400,
	                            "Bad HTTP/0.9 request type (%s)" % `command`)
				return
		else:
			self.send_error(400, "Bad request syntax (%s)" % `requestline`)
			return
		self.command, self.path, self.request_version = command, path, version
		self.headers = self.MessageClass(self.rfile, 0)
		self.infp.write(str(self.headers))
		# test authentification
		global UserName, PassWord
		self.db_name=self.path.split('/')[1]
		UserName, PassWord = 'root',''
		if self.db_name!='':
			if self.DO_AUTH:
				try:
					a=self.headers["Authorization"]
					m,up=string.split(a)
					up2=base64.decodestring(up)
					user,pw=string.split(up2,":")
					UserName, PassWord = user,pw
					if not self.get_userinfo(user,pw):
						self.send_autherror(401,"Authorization Required"); return
				except Exception ,e:
					print e
					self.send_autherror(401,"Authorization Required")
					return

		# check for methods starting with do_
		mname = 'do_' + command
		if not hasattr(self, mname):
			self.send_error(501, "Unsupported method (%s)" % `command`)
			return

		method = getattr(self, mname)
		method()

		self.infp.flush()
		self.infp.close()
		self._flush()

class tinyerp_auth(DAVRequestHandler):
	verbose = False
	def get_userinfo(self,user,pw):
		print '\tAuth', user, pw
		print '-'*80
		if not self.db_name or self.db_name=='':
			self.db_name=self.path.split('/')[1]
			user='root'
			pw=''

		db,pool = pooler.get_db_and_pool(self.db_name)
		res = security.login(self.db_name, user, pw)
		print '\tAuth', user, pw, res
		if res:
			auth['user']=user
			auth['pwd']=pw
		return bool(res)
