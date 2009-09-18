# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (C) P. Christeas, 2009, all rights reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import os
import tools

""" The algorithm of data storage

We have to consider 3 cases of data /retrieval/:
 Given (context,path) we need to access the file (aka. node).
 given (directory, context), we need one of its children (for listings, views)
 given (ir.attachment, context), we needs its data and metadata (node).

For data /storage/ we have the cases:
 Have (ir.attachment, context), we modify the file (save, update, rename etc).
 Have (directory, context), we create a file.
 Have (path, context), we create or modify a file.
 
Note that in all above cases, we don't explicitly choose the storage media,
but always require a context to be present.

Note that a node will not always have a corresponding ir.attachment. Dynamic
nodes, for once, won't. Their metadata will be computed by the parent storage
media + directory.

The algorithm says that in any of the above cases, our first goal is to locate
the node for any combination of search criteria. It would be wise NOT to 
represent each node in the path (like node[/] + node[/dir1] + node[/dir1/dir2])
but directly jump to the end node (like node[/dir1/dir2]) whenever possible.

We also contain all the parenting loop code in one function. This is intentional,
because one day this will be optimized in the db (Pg 8.4).


"""

class document_storage(osv.osv):
    """ The primary object for data storage.
    Each instance of this object is a storage media, in which our application
    can store contents. The object here controls the behaviour of the storage
    media.
    The referring document.directory-ies will control the placement of data
    into the storage.
    
    It is a bad idea to have multiple document.storage objects pointing to
    the same tree of filesystem storage.
    """
    _name = 'document.storage'
    _description = 'Document storage media'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=1),
        'write_date': fields.datetime('Date Modified', readonly=True),
        'write_uid':  fields.many2one('res.users', 'Last Modification User', readonly=True),
        'create_date': fields.datetime('Date Created', readonly=True),
        'create_uid':  fields.many2one('res.users', 'Creator', readonly=True),
        'user_id': fields.many2one('res.users', 'Owner'),
        'group_ids': fields.many2many('res.groups', 'document_directory_group_rel', 'item_id', 'group_id', 'Groups'),
        'dir_ids': fields.one2many('document.directory', 'parent_id', 'Directories'),
        'type': fields.selection([('db','Database'),('filestore','Internal File storage'),
		('realstore','External file storage'), ('virtual','Virtual storage')], 'Type', required=True),
	'path': fields.char('Path',size=250,select=1,help="For file storage, the root path of the storage"),
	'online': fields.boolean('Online',help="If not checked, media is currently offline and its contents not available", required=True),
	'readonly': fields.boolean('Read Only', help="If set, media is for reading only"),
    }

    def _get_rootpath(self,cr,uid,context=None):
	from tools import config
        return os.path.join(tools.config['root_path'], 'filestore', cr.dbname)

    _defaults = {
        'user_id': lambda self,cr,uid,ctx: uid,
	'online': lambda *args: True,
	'readonly': lambda *args: False,
        # Note: the defaults below should only be used ONCE for the default
        # storage media. All other times, we should create different paths at least.
        'type': lambda *args: 'filestore',
        'path': _get_rootpath,
    }
    _sql_constraints = [
	# SQL note: a path = NULL doesn't have to be unique.
	('path_uniq', 'UNIQUE(type,path)', "The storage path must be unique!")
	]
	
    def get_data_n(self, cr,uid, id, file_node,context = None):
	""" retrieve the contents of some file_node having storage_id = id
	"""
        print "storage.get_data"
	if not context:
		context = {}
        boo = self.browse(cr,uid,id,context)
	ira = self.pool.get('ir.attachment').browse(cr,uid, file_node.file_id, context=context)
	return self.__get_data_3(cr,uid,boo, ira, context)
	

    def get_data_i(self, cr, uid, ira_id, context = None):
	if not context:
		context = {}
	ira_o = self.pool.get('ir.attachment')
	ira = ira_o.browse(cr,uid,ira_id, context=context)
	boo = ira.parent_id.storage_id
	return self.__get_data_3(cr, uid, boo, ira, context)
	
	
    def __get_data_3(self,cr,uid, boo, ira, context):
	if not boo.online:
		raise RuntimeError('media offline')
	if boo.type == 'filestore':
		fpath = os.path.join(boo.path,ira.store_fname)
		print "Trying to read \"%s\".."% fpath
		return file(fpath,'rb').read()
	elif boo.type == 'db':
		# base64?
		return ira.db_datas
	elif boo.type == 'realstore':
		# fpath = os.path.join(boo.path,
		return None
	else:
		raise TypeError("No %s storage" % boo.type)

document_storage()


#eof