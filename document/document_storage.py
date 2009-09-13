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
    
    def _get_rootpath(self,cr,uid,context=None):
	from tools import config
	from ...
	return config['root_path']+'filestore'



#eof