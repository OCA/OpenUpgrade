##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

from osv import fields
from osv import osv
import time

class payment_type(osv.osv):
    _name = 'payment.type'
    _description = 'Payment type'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
	'suitable_bank_types': fields.many2many('res.partner.bank.type',
						'bank_type_payment_type_rel',
						'pay_type_id','bank_type_id',
						'Suitable bank types')
                }

    def suitable_bank_account_code(self,cr,uid,type_name,context):
        t = self.pool.get('res.partner.bank.type')
        return t.read(cr,uid,t.search(cr,uid,[]),['code'],context=context)
    
payment_type()


def type_get(self, cr, uid, context={}):
    pay_type_obj = self.pool.get('payment.type')
    ids = pay_type_obj.search(cr, uid, [])
    res = pay_type_obj.read(cr, uid, ids, ['code','name'], context)
    return [(r['name'],r['name']) for r in res]+[('','')] 


class payment_order(osv.osv):
    _name = 'payment.order'
    _description = 'Payment Order'

    def type_get(self, cr, uid, context={}):
        pay_type_obj = self.pool.get('payment.type')
        ids = pay_type_obj.search(cr, uid, [])
        res = pay_type_obj.read(cr, uid, ids, ['code','name'], context)
        return [(r['name'],r['name']) for r in res]

    _rec_name = 'date'
    _columns = {
        'date': fields.date('Payment Date',size=64),
        'type': fields.selection(type_get, 'Payment Type'),
        'state': fields.selection([('draft', 'Draft'),('open','Open'),
				   ('cancel','Cancelled'),('done','Done')], 'State'),
        'payment_lines': fields.one2many('payment.line','order','Payment Lines')

    }
    _defaults = {
	'date': time.strftime('%Y-%m-%d'),
	'state': lambda *a: 'draft',
       }

payment_order()

class payment_line(osv.osv):
    _name = 'payment.line'
    _description = 'Payment Line'
    _rec_name = 'move_line'
    _columns = {
        'move_line': fields.many2one('account.move.line','Entry Line',required=True),
        'amount': fields.float('Payment Amount', digits=(16,4)),
	'type': fields.selection(type_get, 'Payment Type',required=True),
	'bank': fields.many2one('res.partner.bank','Bank Account'),
        'order': fields.many2one('payment.order','Order', ondelete='cascade', select=True),
     }
    def onchange_move_line(self, cr, uid, id, move_line, context={}):
        if not move_line:
            return {}
        line=self.pool.get('account.move.line').browse(cr,uid,move_line)
        return {'value': {'amount': line.debit}}

payment_line()
