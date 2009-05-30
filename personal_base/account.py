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
from base import base_delete_unit_test_records, base_get_default_currency
import datetime

class personal_account_type(osv.osv):
    _name = "personal.base.account.type"
    _description = "Account Type"
    _order = "name"
    _columns = {
        'name': fields.char('Acc. Type Name', size=64, required=True, translate=True),
        'sign': fields.selection([(-1, 'Negative'), (1, 'Positive')], 'Sign', required=True),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique !')
    ]
    
    #demo data
    #EQU_ID = 1
    #ASS_ID = 2
    #LIA_ID = 3
    #INC_ID = 4
    #EXP_ID = 5
    
    def try_create_demo(self, cr, uid):
        pass
        #if self.search(cr, uid, []) == []:
        #    self.create(cr, uid, {'name': 'Begin balance', 'sign': 1})
        #    self.create(cr, uid, {'name': 'Asset', 'sign': 1})
        #    self.create(cr, uid, {'name': 'Liability', 'sign': -1})
        #    self.create(cr, uid, {'name': 'Income', 'sign': -1})
        #    self.create(cr, uid, {'name': 'Expense', 'sign': 1})
            #self.pool.get('ir.model.data')._update(cr, uid, self._name, 'personal_base', {'name': 'Begin balance'}, 'TYPE_EQU_ID')
        
personal_account_type()

class personal_account(osv.osv):
    _name = "personal.base.account"
    _description = "Account"
    _order = "name"
    
#    def _account_type_code_get(self, cr, uid, context={}):
#        acc_type_obj = self.pool.get('personal.base.account.type')
#        ids = acc_type_obj.search(cr, uid, [])
#        res = acc_type_obj.read(cr, uid, ids, ['id', 'name'], context)
#        return [(r['id'], r['name']) for r in res]

    def _get_balance_fnc(self, cr, uid, ids, prop, unknow_none, context):
        currency_pool = self.pool.get('res.currency')
        res = {}
        cr.execute(("SELECT a.id, " \
                    "SUM(COALESCE(l.amount_base, 0)) " \
                "FROM personal_base_account a " \
                    "LEFT JOIN personal_base_account_entry_line l " \
                    "ON (a.id=l.account_id) " \
                "WHERE l.state = 'confirmed' " \
                    "AND a.id IN (%s) " \
                "GROUP BY a.id") % (','.join(map(str,ids)),))
        for id in ids:
            res[id] = 0
        for account_id, sum in cr.fetchall():
            account = self.browse(cr, uid, account_id)
            res[account_id] = currency_pool.round(cr, uid, account.currency_id, sum * account.type_id.sign)
        
        #line_pool = self.pool.get('personal.base.account.entry.line')
        #for id in ids:
        #    account = self.browse(cr, uid, id)
        #    res[id] = 0.0
        #    for search_line_id in line_pool.search(cr, uid, 
        #            [('account_id', '=', id),
        #             ('state', '=', 'confirmed'),]
        #    ):
        #        line = line_pool.browse(cr, uid, search_line_id)
        #        res[id] = res[id] + (line.amount_base * account.type_id.sign)
        return res

    _columns = {
        'user_id': fields.many2one('res.users', 'User', required=True),
        'name': fields.char('Name', size=128, required=True, select=True),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'type_id': fields.many2one('personal.base.account.type', 'Account Type', required=True),
        'parent_id': fields.many2one('personal.base.account', 'Parent Code', select=True),
        'child_ids': fields.one2many('personal.base.account', 'parent_id', 'Childs Codes'),
        'note': fields.text('Note'),
        'balance': fields.function(_get_balance_fnc, method=True, type="float", digits=(10,2), string='Balance'),
        
        #fields for unit_test
        'unit_test': fields.boolean(string='unit_test')
    }

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'currency_id': lambda self, cr, uid, context: base_get_default_currency(cr, uid, context),
        'unit_test': lambda *a: False,
    }
    
    def search(self, cr, uid, args, offset=0, limit=2000, order=None, context=None, count=False):
        args.append(('user_id','=',uid))
        return osv.orm.orm.search(self, cr, uid, args, offset, limit, order,
                context=context)
    
    #for unit tests
    def try_create_litas(self, cr, uid):
        cur_pool = self.pool.get('res.currency')
        cur_rate_pool = self.pool.get('res.currency.rate')
        if cur_pool.search(cr, uid, [('code','=','LTL')]) == []:
            cur_id = cur_pool.create(cr, uid, {'code': 'LTL', 'name': 'Litas', 
                'rounding': 0.01, 'accuracy': 4})
            cur_rate_pool.create(cr, uid, {'currency_id': cur_id, 'rate': 3.4528, 
                'name': datetime.date(2002,2,2)})
    
    def delete_unit_test_records(self, cr, uid):
        base_delete_unit_test_records(self, cr, uid)
            
personal_account()
