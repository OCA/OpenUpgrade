# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Sandas. (http://www.sandas.eu) All Rights Reserved.
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

from osv import fields, osv
from base import base_delete_unit_test_records

class users(osv.osv):
    _name = "res.users"
    _description = "User Preferences"
    _inherit = 'res.users'
    _columns = {
        'email': fields.char('E-Mail Address', size=255, required=True),
        'currency_id': fields.many2one('res.currency', 'Default Currency', required=True),
        'created': fields.datetime('Created'),
        'first_login': fields.boolean('First Login', required=True),
        
        'unit_test': fields.boolean('unit_test'),
    }
    
    _defaults = {
        'first_login': lambda *a: True,
        'unit_test': lambda *a: False,
    }
    
    #for unit tests
    def delete_unit_test_records(self, cr, uid):
        base_delete_unit_test_records(self, cr, uid)
    
    def try_create(self, cr, uid, collumns):
        if self.search(cr, uid, ['login','=',collumns['login']]) == []:
            new_id = self.create(cr, uid, collumns)

users()
