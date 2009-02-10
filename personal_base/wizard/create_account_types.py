# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2008 Sandas. (http://www.sandas.eu) All Rights Reserved.
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
############################################################

import wizard
import pooler

class wiz_create_account_types(wizard.interface):
    def _create_account_types(self, cr, uid, data, context):
        type_pool = pooler.get_pool(cr.dbname).get('personal.base.account.type')
        if type_pool.search(cr, uid, []) != []:
            raise wizard.except_wizard('Error', 'Account types table must be empty before creating default account types !')
        
        type_pool.create(cr, uid, {'name': 'Begin balance', 'sign': 1})
        type_pool.create(cr, uid, {'name': 'Asset', 'sign': 1})
        type_pool.create(cr, uid, {'name': 'Liability', 'sign': -1})
        type_pool.create(cr, uid, {'name': 'Income', 'sign': -1})
        type_pool.create(cr, uid, {'name': 'Expense', 'sign': 1})
        
        return {
            'name': 'Types',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'personal.base.account.type',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
    states = {
        'init': {
            'actions': [],
            'result': {'type':'action', 'action':_create_account_types, 'state':'end'}
        }
    }
wiz_create_account_types('personal.base.account.create_account_types')
