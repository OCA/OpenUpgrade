from DAV.WebDAVServer import DAVRequestHandler
import sys
import pooler
from service import security

class tinyerp_auth(DAVRequestHandler):
	verbose = False
	def get_userinfo(self,user,pw):
		db,pool = pooler.get_db_and_pool(self.db_name)
		res = security.login(self.db_name, user, pw)
		return bool(res)
