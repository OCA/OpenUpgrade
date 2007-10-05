##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from webdav.content_index import content_index
import base64

from osv import osv, fields
import urlparse

import webdav
import webdav.DAV.errors

import pooler

class node_class(object):
	def __init__(self, cr, uid, path, object, object2=False, context={}, content=False, type='collection'):
		self.cr = cr
		self.uid = uid
		self.path = path
		self.object = object
		self.object2 = object2
		self.context = context
		self.content = content
		self.type=type

	def _file_get(self, nodename=False):
		pool = pooler.get_pool(self.cr.dbname)
		fobj = pool.get('ir.attachment')
		res2 = []
		where = []
		if self.object2:
			where.append( ('res_model','=',self.object2._name) )
			where.append( ('res_id','=',self.object2.id) )
			for content in self.object.content_ids:
				if not nodename:
					n = node_class(self.cr, self.uid,  self.path+'/'+self.object2.name+content.suffix, self.object2, False, content=content, type='content')
					res2.append( n)
				else:
					if nodename == self.object2.name + content.suffix:
						n = node_class(self.cr, self.uid,  self.path+'/'+self.object2.name+content.suffix, self.object2, False, content=content, type='content')
						res2.append(n)
		else:
			where.append( ('parent_id','=',self.object.id) )
			where.append( ('res_id','=',False) )
		if nodename:
			where.append( (fobj._rec_name,'=',nodename) )
		ids = fobj.search(self.cr, self.uid, where, context=self.context)
		res = fobj.browse(self.cr, self.uid, ids, context=self.context)
		return map(lambda x: node_class(self.cr, self.uid, self.path+'/'+x.name.replace('/','_'), x, False, type='file'), res) + res2

	def _child_get(self, nodename=False):
		if self.type<>'collection':
			return []
		if self.object.type=='directory':
			where = []
			if nodename:
				where.append(('name','=',nodename))
			where.append(('parent_id','=',self.object.id))
			ids = self.object.search(self.cr, self.uid, where, self.context)
			res = self.object.browse(self.cr, self.uid, ids,self.context)
			return map(lambda x: node_class(self.cr, self.uid, self.path+'/'+x.name.replace('/','_'), x, False), res)
		elif self.object.type=="ressource":

			where = []
			if nodename:
				where.append(('name','=',nodename))

			obj = self.object2
			if not self.object2:
				pool = pooler.get_pool(self.cr.dbname)
				obj = pool.get(self.object.ressource_type_id.model)

			if self.object.ressource_tree:
				# Todo change False by selected parent
				where.append((obj._parent_name,'=',self.object2 and self.object2.id or False))
			else:
				if self.object2:
					return []

			ids = obj.search(self.cr, self.uid, where, self.context)
			res = obj.browse(self.cr, self.uid, ids,self.context)
			return map(lambda x: node_class(self.cr, self.uid, self.path+'/'+x.name.replace('/','_'), self.object, x), res)

		else:
			print "*** Directory type", self.object.type, "not implemented !"
			print self.type, nodename, self.object, self.object2


	def children(self):
		return self._child_get() + self._file_get()

	def child(self, name):
		res = self._child_get(name)
		if res:
			return res[0]
		res = self._file_get(name)
		if res:
			return res[0]
		raise webdav.DAV.errors.DAV_NotFound

	def parent(self):
		return node_class(True)

	def name_get(self):
		if self.object.parent_id:
			return self.object.name
		return '/'

	def path_get(self):
		path = self.path
		if self.path[0]=='/':
			path = self.path[1:]
		return path

class document_directory(osv.osv):
	_name = 'document.directory'
	_description = 'Document directory'
	_columns = {
		'name': fields.char('Name', size=64, required=True, select=1),
		'write_date': fields.datetime('Date Modified', readonly=True),
		'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
		'create_date': fields.datetime('Date Created', readonly=True),
		'create_uid':  fields.many2one('res.users', 'Creator', readonly=True),
		'file_type': fields.char('Content Type', size=32),
		'user_id': fields.many2one('res.users', 'Owner'),
		'group_ids': fields.many2many('res.groups', 'document_directory_group_rel', 'item_id', 'group_id', 'Groups'),
		'parent_id': fields.many2one('document.directory', 'Parent Item'),
		'child_ids': fields.one2many('document.directory', 'parent_id', 'Childs'),
		'file_ids': fields.one2many('ir.attachment', 'parent_id', 'Files'),
		'content_ids': fields.one2many('document.directory.content', 'directory_id', 'Content'),
		'type': fields.selection([('directory','Static Directory'),('link','Link to Another Directory'),('ressource','Other Ressources')], 'Type', required=True),
		'ressource_type_id': fields.many2one('ir.model', 'Ressource Model'),
		'ressource_tree': fields.boolean('Tree Structure'),
	}
	_defaults = {
		'user_id': lambda self,cr,uid,ctx: uid,
		'type': lambda *args: 'directory'
	}
	_sql_constraints = [
		('filename_uniq', 'unique (name,parent_id)', 'The directory name must be unique !')
	]
	def _get_childs(self, cr, uid, node, nodename=False, context={}):
		where = []
		if nodename:
			where.append(('name','=',nodename))
		if object:
			where.append(('parent_id','=',object.id))
		ids = self.search(cr, uid, where, context)
		return self.browse(cr, uid, ids, context), False

	"""
		PRE:
			uri: of the form "Sales Order/SO001"
		PORT:
			uri
			object: the object.directory or object.directory.content
			object2: the other object linked (if object.directory.content)
	"""
	def get_object(self, cr, uid, uri, root, context={}):
		node = node_class(cr, uid, '/', root)
		if not uri:
			return node
		uris = uri.split('/')
		while len(uris):
			path = uris.pop(0)
			if path:
				node = node.child(path)
		return node

	def get_childs(self, cr, uid, uri, root, context={}):
		node = self.get_object(cr, uid, uri, root, context)
		children = node.children()
		result = map(lambda node: node.path_get(), children)
		#childs,object2 = self._get_childs(cr, uid, object, False, context)
		#result = map(lambda x: urlparse.urljoin(path+'/',x.name), childs)
		return result

	def create(self, cr, user, vals, context=None):
		if vals.get('name',False) and (vals.get('name').find('/')+1 or vals.get('name').find('@')+1 or vals.get('name').find('$')+1 or vals.get('name').find('#')+1) :
			raise webdav.DAV.errors.DAV_NotFound('Directory name must not contain special character...')
		return super(document_directory,self).create(cr, user, vals, context)

document_directory()

class document_repository(osv.osv):
	_name = 'document.repository'
	_description = 'Document repository'
	_columns = {
		'name': fields.char('Name', size=64, required=True, select=1),
		'note': fields.text('Notes'),
		'active': fields.boolean('Active'),
		'server_url': fields.char('Serveur Host', size=64, required=True, select=1),
		'server_port': fields.integer('Serveur Port', required=True, select=1),
		'directory_id': fields.many2one('document.directory', 'Root Directory', required=True),
	}
	_defaults = {
		'server_url': lambda *args: 'localhost',
		'active': lambda *args: True,
		'server_port': lambda *args: 8008
	}
	_sql_constraints = [
		('name_uniq', 'unique (name)', 'The repository name must be unique !'),
		('server_port_uniq', 'unique (server_url,server_port)', 'You can not create two repositories on the same port !')
	]
document_repository()

class document_directory_content(osv.osv):
	_name = 'document.directory.content'
	_description = 'Directory Content'
	_order = "sequence"
	_columns = {
		'name': fields.char('Content Name', size=64, required=True),
		'sequence': fields.integer('Sequence', size=16),
		'suffix': fields.char('Suffix', size=16),
		'versioning': fields.boolean('Versioning'),
		'report_id': fields.integer('Report'),
		'extension': fields.selection([('.pdf','.pdf'),('','None')], 'Extension', required=True),
		'directory_id': fields.many2one('document.directory', 'Directory')
	}
	_defaults = {
		'extension': lambda *args: '',
		'sequence': lambda *args: 1
	}
document_directory_content()


class document_file(osv.osv):
	_inherit = 'ir.attachment'
	_columns = {
#		'name': fields.char('Name', size=64, required=True, select=1),
#		'datas': fields.binary('Content'), # datas
#		'datas_fname': fields.char('File Name', size=128, required=True), # datas_fname
#		'res_model': fields.char('Attached Model', size=64), #res_model
#		'res_id': fields.integer('Attached ID'), #res_id

		'user_id': fields.many2one('res.users', 'Owner', select=1),
		'group_ids': fields.many2many('res.groups', 'document_directory_group_rel', 'item_id', 'group_id', 'Groups'),
		'parent_id': fields.many2one('document.directory', 'Directory', select=1),
		'file_size': fields.integer('File Size', required=True),
		'file_type': fields.char('Content Type', size=32),
		'index_content': fields.text('Indexed Content', select=1),
		'write_date': fields.datetime('Date Modified', readonly=True),
		'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
		'create_date': fields.datetime('Date Created', readonly=True),
		'create_uid':  fields.many2one('res.users', 'Creator', readonly=True),
	}
	_defaults = {
		'user_id': lambda self,cr,uid,ctx:uid,
		'file_size': lambda self,cr,uid,ctx:0
	}
	_sql_constraints = [
		#('filename_uniq', 'unique (datas_fname,parent_id)', 'The filename must be unique !')
	]

	def create(self, cr, user, vals, context=None):
		vals['file_size']= len(vals['datas'])
		vals['index_content']= content_index(base64.decodestring(vals['datas']), vals['name'], None)
		vals['file_type']= vals['name'].split('.')[1] or False
		return super(document_file,self).create(cr, user, vals, context)


document_file()


