import pooler

import base64
import sys
import os
import time
from string import joinfields, split, lower

from DAV import AuthServer
from service import security
import dav_auth

import netsvc
import urlparse
from content_index import content_index

from DAV.constants import COLLECTION, OBJECT
from DAV.errors import *
from DAV.iface import *

from DAV.davcmd import copyone, copytree, moveone, movetree, delone, deltree

class tinyerp_handler(dav_interface):
	"""
	This class models a Tiny ERP interface for the DAV server
	"""
	def __init__(self,  host,port,  verbose=False):
		self.db_name = False
		self.directory_id=False
		self.host=host
		self.port=port
		self.baseuri = 'http://%s:%s/' % (self.host, self.port)
		self.db_name_list=[]
#
#
#	def get_db(self,uri):
#		names=self.uri2local(uri).split('/')
#		self.db_name=False
#		if len(names) > 1:
#			self.db_name=self.uri2local(uri).split('/')[1]
#			if self.db_name=='':
#				raise Exception,'Plese specify Database name in folder'
#		return self.db_name
#

	def is_db(self, uri):
		reluri = self.uri2local(uri)
		return not len(reluri.split('/'))>1

	def db_list(self):
		s = netsvc.LocalService('db')
		result = s.list()
		self.db_name_list=[]
		for db_name in result:
			db = pooler.get_db_only(db_name)
			cr = db.cursor()
			cr.execute("select id from ir_module_module where name = 'document'")
			res=cr.fetchone()
			if res and len(res):
				self.db_name_list.append(db_name)
				cr.close()
		#result = ['trunk']
		return self.db_name_list

	def get_childs(self,uri):
		""" return the child objects as self.baseuris for the given URI """
		print 'GET Childs', uri
		if self.is_db(uri):
			s = netsvc.LocalService('db')
			return map(lambda x: urlparse.urljoin(self.baseuri, x), self.db_list())
		result = []
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		for d in node.children():
			print 'XXX result',d, node
			result.append( urlparse.urljoin(self.baseuri, d.path) )
		return result

	def uri2local(self, uri):
		uparts=urlparse.urlparse(uri)
		reluri=uparts[2]
		if reluri and reluri[-1]=="/":
			reluri=reluri[:-1]
		return reluri

	#
	# pos: -1 to get the parent of the uri
	#
	def get_cr(self, uri):
		reluri = self.uri2local(uri)
		dbname = reluri.split('/')[1]
		uid = security.login(dbname, 'admin', 'admin')
		db,pool = pooler.get_db_and_pool(dbname)
		cr = db.cursor()
		uri2 = reluri.split('/')[1:]
		return cr, uid, pool, uri2

	def uri2object(self, cr,uid, pool,uri):
		node = pool.get('document.directory').get_object(cr, uid, uri)
		return node

	def mkcol(self,uri):
		""" create a new collection """
		if self.is_db(uri):
			raise DAV_Error, 409
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2[:-1])
		print 'Found', node

		# TODO: Test Permissions
		if not node:
			print 'ICI', 409
			raise DAV_Error,409

		objname = uri2[-1]
		pool.get('document.directory').create(cr, uid, {
			'name': objname,
			'parent_id': node.object.id,
			'ressource_type_id': node.object.ressource_type_id.id,
			'ressource_id': node.object2 and node.object2.id or False
		})
		cr.commit()
		cr.close()
		return 201

	def get_data(self,uri):
		if self.is_db(uri):
			raise DAV_Error, 409
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		if not node:
			raise DAV_NotFound
		if node.type=='file':
			return base64.decodestring(node.object.datas or '')
		elif node.type=='content':
			report = pool.get('ir.actions.report.xml').browse(cr, uid, node.content['report_id']['id'])
			srv = netsvc.LocalService('report.'+report.report_name)
			pdf,pdftype = srv.create(cr, uid, [node.object.id], {}, {})
			return pdf
		else:
			raise DAV_Forbidden

	def _get_dav_resourcetype(self,uri):
		""" return type of object """
		print 'RT', uri
		if self.is_db(uri):
			return COLLECTION
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		cr.close()
		if node.type in ('collection','database'):
			return COLLECTION
		return OBJECT

	def _get_dav_displayname(self,uri):
		raise DAV_Secret

	def _get_dav_getcontentlength(self,uri):
		""" return the content length of an object """
		print 'Get DAV CL', uri
		if self.is_db(uri):
			return '0'
		result = 0
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr, uid, pool, uri2)
		if node.type=='file':
			result = node.object.file_size or 0
		cr.close()
		return str(result)

	def get_lastmodified(self,uri):
		""" return the last modified date of the object """
		print 'Get DAV Mod', uri
		today = time.time()
		return today
		if self.is_db(uri):
			return today

		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		if node.type=='file':
			dt = node.object.write_date or node.object.create_date
			result = int(time.mktime(time.strptime(dt,'%Y-%m-%d %H:%M:%S')))
		else:
			result = today
		cr.close()
		return result

	def get_creationdate(self,uri):
		""" return the last modified date of the object """
		print 'Get DAV Cre', uri
		if self.is_db(uri):
			raise DAV_Error, 409
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)

		if node.type=='file':
			result = node.object.write_date or node.object.create_date
		else:
			result = time.strftime('%Y-%m-%d %H:%M:%S')
		cr.close()
		return time.mktime(time.strptime(result,'%Y-%m-%d %H:%M:%S'))

	def _get_dav_getcontenttype(self,uri):
		print 'Get DAV CT', uri
		if self.is_db(uri):
			return 'httpd/unix-directory'
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		result = 'application/octet-stream'
		if node.type=='collection':
			result = 'httpd/unix-directory'
		cr.close()
		return result
		#raise DAV_NotFound, 'Could not find %s' % path

	def put(self,uri,data,content_type=None):
		""" put the object into the filesystem """
		if self.is_db(uri):
			raise DAV_Forbidden
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2[:-1])

		objname = uri2[-1]
		fobj = pool.get('ir.attachment')
		ext =False
		if objname.find('.') >0 :
			ext = objname.split('.')[1] or False
		val = {
			'name': objname,
			'datas_fname': objname,
			'file_size': len(data),
			'datas': base64.encodestring(data),
			'file_type': ext,
			'parent_id': node.object and node.object.id or False,
		}
		if node.object2:
			val.update( {
				'res_model': node.object2._name,
				'res_id': node.object2.id
			})
		cid = fobj.create(cr, uid, val)
		cr.commit()

		# TODO: Test Permissions
		if False:
			raise DAV_Forbidden
		cr.close()
		return 201

	def rmcol(self,uri):
		""" delete a collection """
		if self.is_db(uri):
			raise DAV_Error, 409
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)

		if node.object._table_name=='document.directory':
			if node.object.child_ids:
				raise DAV_Forbidden # forbidden
			if node.object.file_ids:
				raise DAV_Forbidden # forbidden
			res = pool.get('document.directory').unlink(cr, uid, [node.object.id])
		cr.commit()
		cr.close()
		return 204

	def rm(self,uri):
		if self.is_db(uri):
			raise DAV_Error, 409
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		if not node:
			raise DAV_NotFound, 404

		if node.object._table_name=='ir.attachment':
			res = pool.get('ir.attachment').unlink(cr, uid, [node.object.id])
		else:
			raise DAV_Forbidden # forbidden
		cr.commit()
		cr.close()
		return 204

	### DELETE handlers (examples)
	### (we use the predefined methods in davcmd instead of doing
	### a rm directly
	###

	def delone(self,uri):
		""" delete a single resource

		You have to return a result dict of the form
		uri:error_code
		or None if everything's ok

		"""
		return delone(self,uri)

	def deltree(self,uri):
		""" delete a collection

		You have to return a result dict of the form
		uri:error_code
		or None if everything's ok
		"""

		return deltree(self,uri)


	###
	### MOVE handlers (examples)
	###

	def moveone(self,src,dst,overwrite):
		""" move one resource with Depth=0

		an alternative implementation would be

		result_code=201
		if overwrite:
			result_code=204
			r=os.system("rm -f '%s'" %dst)
			if r: return 412
		r=os.system("mv '%s' '%s'" %(src,dst))
		if r: return 412
		return result_code

		(untested!). This would not use the davcmd functions
		and thus can only detect errors directly on the root node.
		"""
		return moveone(self,src,dst,overwrite)

	def movetree(self,src,dst,overwrite):
		""" move a collection with Depth=infinity

		an alternative implementation would be

		result_code=201
		if overwrite:
			result_code=204
			r=os.system("rm -rf '%s'" %dst)
			if r: return 412
		r=os.system("mv '%s' '%s'" %(src,dst))
		if r: return 412
		return result_code

		(untested!). This would not use the davcmd functions
		and thus can only detect errors directly on the root node"""

		return movetree(self,src,dst,overwrite)

	###
	### COPY handlers
	###

	def copyone(self,src,dst,overwrite):
		""" copy one resource with Depth=0

		an alternative implementation would be

		result_code=201
		if overwrite:
			result_code=204
			r=os.system("rm -f '%s'" %dst)
			if r: return 412
		r=os.system("cp '%s' '%s'" %(src,dst))
		if r: return 412
		return result_code

		(untested!). This would not use the davcmd functions
		and thus can only detect errors directly on the root node.
		"""
		return copyone(self,src,dst,overwrite)

	def copytree(self,src,dst,overwrite):
		""" copy a collection with Depth=infinity

		an alternative implementation would be

		result_code=201
		if overwrite:
			result_code=204
			r=os.system("rm -rf '%s'" %dst)
			if r: return 412
		r=os.system("cp -r '%s' '%s'" %(src,dst))
		if r: return 412
		return result_code

		(untested!). This would not use the davcmd functions
		and thus can only detect errors directly on the root node"""

		return copytree(self,src,dst,overwrite)

	###
	### copy methods.
	### This methods actually copy something. low-level
	### They are called by the davcmd utility functions
	### copytree and copyone (not the above!)
	### Look in davcmd.py for further details.
	###

	def copy(self,src,dst):
		ct = self._get_dav_getcontenttype(src)
		data = self.get_data(src)
		self.put(dst,data,ct)
		return 201

	def copycol(self,src,dst):
		""" copy a collection.

		As this is not recursive (the davserver recurses itself)
		we will only create a new directory here. For some more
		advanced systems we might also have to copy properties from
		the source to the destination.
		"""
		return self.mkcol(dst)


	def exists(self,uri):
		""" test if a resource exists """
		if self.is_db(uri):
			return True
		result = False
		cr, uid, pool, uri2 = self.get_cr(uri)
		try:
			node = self.uri2object(cr,uid,pool, uri2)
			if node:
				result = True
		except:
			pass
		cr.close()
		print 'Get Exists', uri, result
		return result

	def is_collection(self,uri):
		""" test if the given uri is a collection """
		return self._get_dav_resourcetype(uri)==COLLECTION
