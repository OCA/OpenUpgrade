import pooler

import base64
import sys
import os
import time
from string import joinfields, split, lower

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
	def __init__(self, db_name, uri, directory_id, verbose=False):
		self.db_name = db_name
		self.directory_id = directory_id
		self.baseuri = uri

	def uri_local(self, uri):
		return uri[len(self.baseuri)-1:]

	def get_childs(self,uri):
		""" return the child objects as self.baseuris for the given URI """
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		result = []
		root = dir.browse(cr, 3, self.directory_id)
		for d in dir.get_childs(cr, 3, self.uri2local(uri),root):
			result.append(urlparse.urljoin(self.baseuri, d))
		cr.close()
		return result

	def uri2local(self, uri):
		uparts=urlparse.urlparse(uri)
		reluri=uparts[2]
		if reluri and reluri[-1]=="/":
			reluri=reluri[:-1]
		return reluri

	def uri2object(self,cr,uid,uri):
		pool = pooler.get_pool(self.db_name)
		reluri = self.uri2local(uri)
		root = pool.get('document.directory').browse(cr, uid, self.directory_id)
		node = pool.get('document.directory').get_object(cr, 3, reluri, root)
		return node

	def mkcol(self,uri):
		""" create a new collection """
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')

		uri = self.uri2local(uri)

		objname = uri.split('/')[-1]
		objuri = '/'.join(uri.split('/')[:-1])
		node = self.uri2object(cr, 3, objuri)
		if not node:
			raise DAV_Error, 409

		if node.object.type=='directory':
			dir.create(cr, 3, {
				'name': objname,
				'parent_id': node.object.id
			})
		elif node.object.type=='ressource':
			if not node.object.ressource_tree and node.object2:
				dir.create(cr, 3, {
					'name': objname,
					'parent_id': node.object.id
				})
			else:
				obj = pool.get(node.object.ressource_type_id.model)
				if node.object2:
					value_dict = {'name': objname,obj._parent_name: node.object2.id}
				else:
					value_dict = {'name': objname}
				obj.create(cr, 3, value_dict)
		else:
			print 'Type', node.object.type, 'not implemented !'

		# test if file already exists
		if False:
			raise DAV_Error,405
		# Test Permissions
		if False:
			raise DAV_Forbidden
		cr.commit()
		cr.close()
		return 201

	def get_data(self,uri):
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		uri = self.uri2local(uri)
		node = self.uri2object(cr, 3, uri)
		if not node:
			raise DAV_NotFound
		if node.type=='file':
			return base64.decodestring(node.object.datas or '')
		elif node.type=='content':
			report = pool.get('ir.actions.report.xml').browse(cr, 3,node.content['report_id']['id'])
			srv = netsvc.LocalService('report.'+report.report_name)
			pdf,pdftype = srv.create(cr, 3, [node.object.id], {}, {})
			return pdf
		else:
			raise DAV_Forbidden

	def _get_dav_resourcetype(self,uri):
		""" return type of object """
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		cr.close()
		if node.type=='collection':
			return COLLECTION
		return OBJECT

	def _get_dav_displayname(self,uri):
		raise DAV_Secret

	def _get_dav_getcontentlength(self,uri):
		""" return the content length of an object """
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		result = 0
		if node.type=='file':
			result = node.object.file_size or 0
		cr.close()
		return str(result)

	def get_lastmodified(self,uri):
		""" return the last modified date of the object """
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		if node.type=='file':
			result = node.object.write_date or node.object.create_date
		else:
			result = time.strftime('%Y-%m-%d %H:%M:%S')
		cr.close()
		return time.mktime(time.strptime(result,'%Y-%m-%d %H:%M:%S'))

	def get_creationdate(self,uri):
		""" return the last modified date of the object """
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		if node.type=='file':
			result = node.object.write_date or node.object.create_date
		else:
			result = time.strftime('%Y-%m-%d %H:%M:%S')
		cr.close()
		return time.mktime(time.strptime(result,'%Y-%m-%d %H:%M:%S'))

	def _get_dav_getcontenttype(self,uri):
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		result = 'application/octet-stream'
		if node.type=='collection':
			result = 'httpd/unix-directory'
		cr.close()
		return result
		#raise DAV_NotFound, 'Could not find %s' % path

	def put(self,uri,data,content_type=None):
		""" put the object into the filesystem """
		if not len(data):
			return 201
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()

		print '**** PUT', uri, len(data)
		uri = self.uri2local(uri)
		#node = self.uri2object(cr, 3, uri)
		## test if file already exists
		#if node:
		#	raise DAV_Error,405

		objname = uri.split('/')[-1]
		objuri = '/'.join(uri.split('/')[:-1])
		node = self.uri2object(cr, 3, objuri)

		fobj = pool.get('ir.attachment')
		ext =False
		if objname.find('.') >0 :
			ext = objname.split('.')[1] or False
		val = {
			'name': objname,
			'datas_fname': objname,
			'file_size': len(data),
			'datas': base64.encodestring(data),
			'index_content': content_index(data, objname, content_type or None),
			'file_type': ext,
			'parent_id': node.object and node.object.id or False,
		}
		if node.object2:
			val.update( {
				'res_model': node.object2._name,
				'res_id': node.object2.id
			})
		fobj.create(cr, 3, val)

		# Test Permissions
		if False:
			raise DAV_Forbidden
		cr.commit()
		cr.close()
		return 201

	def rmcol(self,uri):
		""" delete a collection """
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		if node.object._table_name=='document.directory':
			if node.object.child_ids:
				raise DAV_Forbidden # forbidden
			if node.object.file_ids:
				raise DAV_Forbidden # forbidden
			res = pool.get('document.directory').unlink(cr, 3, node.object.id)
		cr.commit()
		cr.close()
		return 204

	def rm(self,uri):
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		if node.object._table_name=='ir.attachment':
			res = pool.get('ir.attachment').unlink(cr, 3, node.object.id)
		cr.commit()
		cr.close()
		return 204
		raise DAV_Forbidden # forbidden

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
		print '**** COPY ****', src, dst
		db,pool = pooler.get_db_and_pool(self.db_name)
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(src), root)
		if not node.type=='file':
			raise DAV_Error, Forbidden
		data = base64.decodestring(node.object.datas)
		ct = node.object.file_type
		cr.close()
		self.put(dst, data, ct)
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
		db,pool = pooler.get_db_and_pool(self.db_name)
		result = False
		cr = db.cursor()
		try:
			node = self.uri2object(cr, 3, uri)
		except:
			return False
		if node:
			result = True
		cr.close()
		return result

	def is_collection(self,uri):
		""" test if the given uri is a collection """
		db,pool = pooler.get_db_and_pool(self.db_name)
		result = False
		cr = db.cursor()
		dir = pool.get('document.directory')
		root = dir.browse(cr, 3, self.directory_id)
		node = dir.get_object(cr, 3, self.uri2local(uri), root)
		if node.object._table_name=='document.directory':
			result = True
		cr.close()
		return result