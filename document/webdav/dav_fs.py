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
import urllib

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
		self._cache={}
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
			cr.execute("select id from ir_module_module where name = 'document' and state='installed' ")
			res=cr.fetchone()
			if res and len(res):
				self.db_name_list.append(db_name)
				cr.close()
		#result = ['trunk']
		return self.db_name_list

	def get_childs(self,uri):
		""" return the child objects as self.baseuris for the given URI """
		if self.is_db(uri):
			s = netsvc.LocalService('db')
			return map(lambda x: urlparse.urljoin(self.baseuri, x), self.db_list())
		result = []
		if uri[-1]=='/':uri=uri[:-1]
		if uri not in self._cache:
			self._cache[uri]={}
		if 'childs' not in 	self._cache[uri]:
			cr, uid, pool, uri2 = self.get_cr(uri)
			node = self.uri2object(cr,uid,pool, uri2)
			for d in node.children():
				print 'XXX result',d, node
				result.append( urlparse.urljoin(self.baseuri, d.path) )
			self._cache[uri]['childs']=result
		result=	self._cache[uri]['childs']
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
		path=self.baseuri + '/'.join(uri)
		node = pool.get('document.directory').get_object(cr, uid, uri)
		uri=path
		if uri[-1]=='/':uri=uri[:-1]
		self._cache[uri]={
				'path':node.path,
				#'object':node.object,
				#'object2':node.object2,
				'context':node.context,
				'content':node.content,
				'type':node.type,
				'root':node.root
				}

		# set Datas in cache
		if node.type=='file':
			self._cache[uri]['datas']=base64.decodestring(node.object.datas or '')
		elif node.type=='content':
			report = pool.get('ir.actions.report.xml').browse(cr, uid, node.content['report_id']['id'])
			srv = netsvc.LocalService('report.'+report.report_name)
			pdf,pdftype = srv.create(cr, uid, [node.object.id], {}, {})
			self._cache[uri]['datas']=pdf

		# set Childs in cache
		result=[]
		for d in node.children():
			result.append( urlparse.urljoin(self.baseuri, d.path) )
		self._cache[uri]['childs']=result

		#set resourcetype in cache
		if node.type in ('collection','database'):
			self._cache[uri]['resourcetype']= COLLECTION
		else:
			self._cache[uri]['resourcetype']= OBJECT

		# set contentlength in cache
		result=0
		if node.type=='file':
			result = node.object.file_size or 0
			self._cache[uri]['contentlength']= str(result)

		# lastmodified date
		result = time.time()
		if node.type=='file':
			dt = node.object.write_date or node.object.create_date
			result = int(time.mktime(time.strptime(dt,'%Y-%m-%d %H:%M:%S')))
		self._cache[uri]['lastmodified']= result

		# creation date
		result = time.strftime('%Y-%m-%d %H:%M:%S')
		if node.type=='file':
			result = node.object.write_date or node.object.create_date
		self._cache[uri]['creationdate']= time.mktime(time.strptime(result,'%Y-%m-%d %H:%M:%S'))

		# content type
		result = 'application/octet-stream'
		if node.type=='collection':
			self._cache[uri]['getcontenttype']= 'httpd/unix-directory'
		self._cache[uri]['getcontenttype']=result



		return node

	def get_data(self,uri):
		if self.is_db(uri):
			raise DAV_Error, 409
		if uri[-1]=='/':uri=uri[:-1]
		if uri not in self._cache:
			self._cache[uri]={}
		if 'datas' not in 	self._cache[uri]:
			cr, uid, pool, uri2 = self.get_cr(uri)
			node = self.uri2object(cr,uid,pool, uri2)
			if not node:
				raise DAV_NotFound
			if node.type=='file':
				self._cache[uri]['datas']=base64.decodestring(node.object.datas or '')
			elif node.type=='content':
				report = pool.get('ir.actions.report.xml').browse(cr, uid, node.content['report_id']['id'])
				srv = netsvc.LocalService('report.'+report.report_name)
				pdf,pdftype = srv.create(cr, uid, [node.object.id], {}, {})
				self._cache[uri]['datas']=pdf
			else:
				raise DAV_Forbidden
		return self._cache[uri]['datas']

	def _get_dav_resourcetype(self,uri):
		""" return type of object """
		print 'RT', uri
		if uri[-1]=='/':uri=uri[:-1]
		if uri not in self._cache:
			self._cache[uri]={}
		if 'resourcetype' not in 	self._cache[uri]:
			if self.is_db(uri):
				self._cache[uri]['resourcetype']= COLLECTION
				return self._cache[uri]['resourcetype']
			cr, uid, pool, uri2 = self.get_cr(uri)
			node = self.uri2object(cr,uid,pool, uri2)
			cr.close()
			if node.type in ('collection','database'):
				self._cache[uri]['resourcetype']= COLLECTION
				return self._cache[uri]['resourcetype']
			self._cache[uri]['resourcetype']= OBJECT
		return self._cache[uri]['resourcetype']

	def _get_dav_displayname(self,uri):
		raise DAV_Secret

	def _get_dav_getcontentlength(self,uri):
		""" return the content length of an object """
		print 'Get DAV CL', uri
		if uri[-1]=='/':uri=uri[:-1]
		if uri not in self._cache:
			self._cache[uri]={}
		if 'contentlength' not in 	self._cache[uri]:
			if self.is_db(uri):
				self._cache[uri]['contentlength']= '0'
				return self._cache[uri]['contentlength']
			result = 0
			cr, uid, pool, uri2 = self.get_cr(uri)
			node = self.uri2object(cr, uid, pool, uri2)
			if node.type=='file':
				result = node.object.file_size or 0
			cr.close()
			self._cache[uri]['contentlength']= str(result)
		return self._cache[uri]['contentlength']

	def get_lastmodified(self,uri):
		""" return the last modified date of the object """
		print 'Get DAV Mod', uri
		if uri[-1]=='/':uri=uri[:-1]
		if uri not in self._cache:
			self._cache[uri]={}
		if 'lastmodified' not in self._cache[uri]:
			today = time.time()
			#return today
			if self.is_db(uri):
				self._cache[uri]['lastmodified']= today
				return self._cache[uri]['lastmodified']

			cr, uid, pool, uri2 = self.get_cr(uri)
			node = self.uri2object(cr,uid,pool, uri2)
			if node.type=='file':
				dt = node.object.write_date or node.object.create_date
				result = int(time.mktime(time.strptime(dt,'%Y-%m-%d %H:%M:%S')))
			else:
				result = today
			cr.close()
			self._cache[uri]['lastmodified']= result
		return self._cache[uri]['lastmodified']

	def get_creationdate(self,uri):
		""" return the last modified date of the object """
		print 'Get DAV Cre', uri

		if self.is_db(uri):
			raise DAV_Error, 409
		if uri[-1]=='/':uri=uri[:-1]
		if uri not in self._cache:
			self._cache[uri]={}
		if 'creationdate' not in self._cache[uri]:
			cr, uid, pool, uri2 = self.get_cr(uri)
			node = self.uri2object(cr,uid,pool, uri2)

			if node.type=='file':
				result = node.object.write_date or node.object.create_date
			else:
				result = time.strftime('%Y-%m-%d %H:%M:%S')
			cr.close()
			self._cache[uri]['creationdate']= time.mktime(time.strptime(result,'%Y-%m-%d %H:%M:%S'))
		return self._cache[uri]['creationdate']
	def _get_dav_getcontenttype(self,uri):
		print 'Get DAV CT', uri
		if uri[-1]=='/':uri=uri[:-1]
		if uri not in self._cache:
			self._cache[uri]={}
		if 'getcontenttype' not in self._cache[uri]:
			if self.is_db(uri):
				self._cache[uri]['getcontenttype']= 'httpd/unix-directory'
				return self._cache[uri]['getcontenttype']
			cr, uid, pool, uri2 = self.get_cr(uri)
			node = self.uri2object(cr,uid,pool, uri2)
			result = 'application/octet-stream'
			if node.type=='collection':
				self._cache[uri]['getcontenttype']= 'httpd/unix-directory'
			cr.close()
			self._cache[uri]['getcontenttype']=result
		return self._cache[uri]['getcontenttype']
		#raise DAV_NotFound, 'Could not find %s' % path

	def mkcol(self,uri):
		""" create a new collection """
		if uri[-1]=='/':uri=uri[:-1]
		if self.is_db(uri):
			raise DAV_Error, 409
		parent='/'.join(uri.split('/')[:-1])
		if not parent.startswith(self.baseuri):
			parent=self.baseuri + ''.join(parent[1:])
		if not uri.startswith(self.baseuri):
			uri=self.baseuri + ''.join(uri[1:])


		#if parent not in self._cache and 'object' not in self._cache[parent]:
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2[:-1])
		object2=node and node.object2 or False
		object=node and node.object or False

		#object2=self._cache[parent]['object2']
		#object=self._cache[parent]['object']
		# TODO: Test Permissions
		if not object:
			print 'ICI', 409
			raise DAV_Error,409

		objname = uri2[-1]
		pool.get('document.directory').create(cr, uid, {
			'name': objname,
			'parent_id': object.id,
			'ressource_type_id': object.ressource_type_id.id,
			'ressource_id': object2 and object2.id or False
		})


		if parent in self._cache:
			if 'childs' not in self._cache[parent]:
				self.get_childs(parent)
			else:
				childs=self._cache[parent]['childs']
				if object.ressource_type_id and not (object2 and object2.id):
					 for child in childs:
					 	if 'childs' not in self._cache[child]:
					 		self.get_childs(child)
					 	cs=self._cache[child]['childs']
					 	uri=child+'/'+objname
					 	if uri not in cs:cs.append(uri)
				elif uri not in childs:childs.append(uri)

		cr.commit()
		cr.close()
		return 201

	def put(self,uri,data,content_type=None):
		""" put the object into the filesystem """
		if self.is_db(uri):
			raise DAV_Forbidden
		parent='/'.join(uri.split('/')[:-1])
		#if parent not  in self._cache and 'object' not in self._cache[parent]:
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2[:-1])
		object2=node and node.object2 or False
		object=node and node.object or False

		#object=self._cache[parent]['object']
		#object2=self._cache[parent]['object2']
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
			'parent_id': object and object.id or False,
		}
		if object2:
			val.update( {
				'res_model': object2._name,
				'res_id': object2.id
			})
		cid = fobj.create(cr, uid, val)
		cr.commit()

		# TODO: Test Permissions
		if False:
			raise DAV_Forbidden
		cr.close()

		if parent in self._cache:
			if 'childs' not in self._cache[parent]:
				self.get_childs(parent)
			childs=self._cache[parent]['childs']
			if uri not in childs:childs.append(uri)
		return 201

	def rmcol(self,uri):
		""" delete a collection """
		if uri[-1]=='/':uri=uri[:-1]
		if self.is_db(uri):
			raise DAV_Error, 409

		#if uri not in self._cache and 'object' not in self._cache[uri]:
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		object2=node and node.object2 or False
		object=node and node.object or False
		#object=self._cache[uri]['object']
		if object._table_name=='document.directory':
			if object.child_ids:
				raise DAV_Forbidden # forbidden
			if object.file_ids:
				raise DAV_Forbidden # forbidden
			res = pool.get('document.directory').unlink(cr, uid, [object.id])

		parent='/'.join(uri.split('/')[:-1])
		if node.object.parent_id and node.object.parent_id.ressource_type_id:
			parent='/'.join(uri.split('/')[:-2])
		if parent in self._cache:
			if 'childs' in self._cache[parent]:
				childs=self._cache[parent]['childs']
				if uri in childs:childs.remove(uri)
				for child in childs:
					if 'childs' in self._cache[child]:
						cs=self._cache[child]['childs']
						col=child+'/'+uri.split('/')[-1]
						if col in cs:cs.remove(col)
		if uri in self._cache:del self._cache[uri]
		cr.commit()
		cr.close()
		return 204

	def rm(self,uri):
		if uri[-1]=='/':uri=uri[:-1]
		if self.is_db(uri):
			raise DAV_Error, 409

		object=False
		#if uri not in self._cache and 'object' not in self._cache[uri]:
		cr, uid, pool, uri2 = self.get_cr(uri)
		node = self.uri2object(cr,uid,pool, uri2)
		object2=node and node.object2 or False
		object=node and node.object or False
		#object=self._cache[uri]['object']
		if not object:
			raise DAV_NotFound, 404

		print ' rm',object._table_name,uri
		if object._table_name=='ir.attachment':
			res = pool.get('ir.attachment').unlink(cr, uid, [object.id])
		else:
			raise DAV_Forbidden # forbidden
		parent='/'.join(uri.split('/')[:-1])
		if parent in self._cache:
			if 'childs' in self._cache[parent]:
				childs=self._cache[parent]['childs']
				if uri in childs:childs.remove(uri)
		if uri in self._cache:del self._cache[uri]
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
		if uri[-1]=='/':uri=uri[:-1]
		res=delone(self,uri)
		parent='/'.join(uri.split('/')[:-1])
		if parent in self._cache:
			if 'childs' in self._cache[parent]:
				childs=self._cache[parent]['childs']
				if uri in childs:childs.remove(uri)
		if uri in self._cache:del self._cache[uri]
		#self._cache.setdefault(uri, {})
		return res

	def deltree(self,uri):
		""" delete a collection

		You have to return a result dict of the form
		uri:error_code
		or None if everything's ok
		"""
		if uri[-1]=='/':uri=uri[:-1]
		res=deltree(self,uri)
		parent='/'.join(uri.split('/')[:-1])
		if parent in self._cache:
			if 'childs' in self._cache[parent]:
				childs=self._cache[parent]['childs']
				if uri in childs:childs.remove(uri)
		if uri in self._cache:del self._cache[uri]
		#self._cache.setdefault(uri, {})
		return res


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
		res=moveone(self,src,dst,overwrite)
		if src[-1]=='/':src=src[:-1]
		if dst[-1]=='/':dst=dst[:-1]
		parent_src='/'.join(src.split('/')[:-1])
		if parent_src in self._cache:
			if 'childs' in self._cache[parent_src]:
				childs=self._cache[parent_src]['childs']
				if src in childs:childs.remove(src)
		if src in self._cache:del self._cache[src]

		parent_dst='/'.join(dst.split('/')[:-1])
		if parent_dst in self._cache:
			if 'childs' not in self._cache[parent_dst]:
				self.get_childs(parent_dst)
			childs=self._cache[parent_dst]['childs']
			if dst not in childs:childs.append(dst)
		if dst not in self._cache:self._cache[dst]={}
		return res

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

		res=movetree(self,src,dst,overwrite)
		if src[-1]=='/':src=src[:-1]
		if dst[-1]=='/':dst=dst[:-1]
		parent_src='/'.join(src.split('/')[:-1])
		if parent_src in self._cache:
			if 'childs' in self._cache[parent_src]:
				childs=self._cache[parent_src]['childs']
				if src in childs:childs.remove(src)
		if src in self._cache:del self._cache[src]

		parent_dst='/'.join(dst.split('/')[:-1])
		if parent_dst in self._cache:
			if 'childs' not in self._cache[parent_dst]:
				self.get_childs(parent_dst)
			childs=self._cache[parent_dst]['childs']
			if dst not in childs:childs.append(dst)
		if dst not in self._cache:self._cache[dst]={}
		return res

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
		print ' ** copy',src,dst
		res=copyone(self,src,dst,overwrite)
		if src[-1]=='/':src=src[:-1]
		if dst[-1]=='/':dst=dst[:-1]

		parent_dst='/'.join(dst.split('/')[:-1])
		if parent_dst in self._cache:
			if 'childs' not in self._cache[parent_dst]:
				self.get_childs(parent_dst)
			childs=self._cache[parent_dst]['childs']
			if dst not in childs:childs.append(dst)
		if dst not in self._cache:self._cache[dst]={}
		return res

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
		res=copytree(self,src,dst,overwrite)
		if src[-1]=='/':src=src[:-1]
		if dst[-1]=='/':dst=dst[:-1]

		parent_dst='/'.join(dst.split('/')[:-1])
		if parent_dst in self._cache:
			if 'childs' not in self._cache[parent_dst]:
				self.get_childs(parent_dst)
			childs=self._cache[parent_dst]['childs']
			if dst not in childs:childs.append(dst)
		if dst not in self._cache:self._cache[dst]={}
		return res

	###
	### copy methods.
	### This methods actually copy something. low-level
	### They are called by the davcmd utility functions
	### copytree and copyone (not the above!)
	### Look in davcmd.py for further details.
	###

	def copy(self,src,dst):
		src=urllib.unquote(src)
		dst=urllib.unquote(dst)
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
		print " copy a collection."
		return self.mkcol(dst)


	def exists(self,uri):
		""" test if a resource exists """
		if self.is_db(uri):
			return True
		result = False
		if uri in self._cache:
			return True
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
