from DAV.WebDAVServer import DAVRequestHandler
import sys
import pooler
from service import security

class tinyerp_auth(DAVRequestHandler):
	verbose = False
	def get_userinfo(self,user,pw):
		print '\tAuth', user, pw
		print '-'*80
		db,pool = pooler.get_db_and_pool('trunk')
		res = security.login('trunk', user, pw)
		print '\tAuth', user, pw, res
		return bool(res)
