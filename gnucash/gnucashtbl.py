# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2008 P. Christeas. All Rights Reserved
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

import netsvc
import time
from osv import osv, fields

class gnucash_index(osv.osv):
    """ This is a simple table that holds the mapping between gnucash objects
      and OpenObject data.
      It is actually modelled after the ir.model.data table.
    """
    _name = 'gnucash.index'
    _inherit = ''
    _rec_name = 'guid'
    _columns = {
        'guid': fields.char('Gnucash UID', required=True, size=64, select=True),
	'parent_book': fields.many2one('gnucash.index', 'Parent book', ondelete='cascade', select=True),
        'model': fields.char('Object', required=True, size=64, select=True),
        'module': fields.char('Module', required=True, size=64),
        'res_id': fields.integer('Resource ID'),
        'noupdate': fields.boolean('Non Updatable'),
        'date_update': fields.datetime('Update Date'),
        'date_init': fields.datetime('Init Date'),
	'to_delete': fields.boolean('Should be deleted', required=True)
        }
    _defaults = {
        'date_init': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_update': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'noupdate': lambda *a: False,
	'to_delete': lambda *a: False
        }

gnucash_index()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
