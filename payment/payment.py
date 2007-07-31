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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA	 02111-1307, USA.
#
##############################################################################

from osv import fields
from osv import osv
import time
import netsvc
class payment_type(osv.osv):
	_name = 'payment.type'
	_description = 'Payment type'
	_columns = {
		'name': fields.char('Name', size=64, required=True),
		'code': fields.char('Code', size=64, required=True,unique=True,select=True),
		'suitable_bank_types': fields.many2many('res.partner.bank.type',
						'bank_type_payment_type_rel',
						'pay_type_id','bank_type_id',
						'Suitable bank types')
				}

	def suitable_bank_types(self,cr,uid,payment_code,context):
		""" Return the codes of the bank type that are suitable for the given payment type"""
		cr.execute(""" select t.code
				   from res_partner_bank_type t
					inner join bank_type_payment_type_rel r on (r.bank_type_id = t.id)
					inner join payment_type p on (r.pay_type_id = p.id)
				   where p.code = %s""", [payment_code])
		return [x[0] for x in cr.fetchall()]
	
payment_type()


def type_get(self, cr, uid, context={}):
	pay_type_obj = self.pool.get('payment.type')
	ids = pay_type_obj.search(cr, uid, [])
	res = pay_type_obj.read(cr, uid, ids, ['code','name'], context)
	return [(r['code'],r['name']) for r in res] + [('manual', 'Manual')]




class payment_order(osv.osv):
	_name = 'payment.order'
	_description = 'Payment Order'
	_rec_name = 'date'

	def _total(self, cr, uid, ids, name, args, context={}):
		if not ids: return {}
		cr.execute("""select o.id, coalesce(sum(amount),0)
				   from payment_order o left join payment_line l on (o.id = l.payment_order)
			   where o.id in (%s) group by o.id"""% ','.join(map(str,ids)))
		return dict(cr.fetchall())

	_columns = {
		'date': fields.date('Payment Date',size=64),
		'type': fields.selection(type_get, 'Payment Type',size=16,required=True, select=True),
		'state': fields.selection([('draft', 'Draft'),('open','Open'),
				   ('cancel','Cancelled'),('done','Done')], 'State', select=True),
		'payment_lines': fields.one2many('payment.line','payment_order','Payment Lines'),
		'total': fields.function(_total, string="Total", method=True, type='float'),
		'journal': fields.many2one('account.journal','Journal',required=True, domain=[('type','=','cash')]),
		'bank': fields.many2one('res.partner.bank','Bank', required=True),
		'user_id': fields.many2one('res.users','User',required=True),
	}

	_defaults = {
		'user_id': lambda self,cr,uid,context: uid, 
		'type': lambda *a : 'manual',
		'state': lambda *a: 'draft',
	   }

	def set_to_draft(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'draft'})
		wf_service = netsvc.LocalService("workflow")
		for id in ids:
			wf_service.trg_create(uid, 'payment.order', id, cr)
		return True

payment_order()

class payment_line(osv.osv):
	_name = 'payment.line'
	_description = 'Payment Line'
	_rec_name = 'move_line'

	def _partner(self, cr, uid, ids, name, args, context={}):
		if not ids: return {}
		cr.execute("""SELECT pl.id, i.partner_id 
						from payment_line pl 
							left join account_move_line ml on (ml.id=pl.move_line) 
							inner join account_move m on (m.id=ml.move_id) 
							inner join account_invoice i on (i.move_id=m.id)
						where pl.id in (%s)"""% ','.join(map(str,ids)))
		return dict(cr.fetchall())

	def translate(self,orig):
		if orig == "to_pay": return "credit"
		return orig

	def select_by_name(self, cr, uid, ids, name, args, context={}):
		if not ids: return {}
		cr.execute("""SELECT pl.id, ml.%s 
						from account_move_line ml 
							inner join payment_line pl on (ml.id= pl.move_line)
						where pl.id in (%s)"""% (self.translate(name),','.join(map(str,ids))) )
		return dict(cr.fetchall())


	_columns = {
		'move_line': fields.many2one('account.move.line','Entry Line',required=True),
		'amount': fields.float('Payment Amount', digits=(16,2), required=True),
		'bank': fields.many2one('res.partner.bank','Bank Account', required=True),
		'payment_order': fields.many2one('payment.order','Order', ondelete='cascade', select=True),
		'partner': fields.function(_partner, string="Partner", method=True, type='many2one', obj='res.partner'),
		'to_pay': fields.function(select_by_name, string="To Pay", method=True, type='float'),
		'date_maturity': fields.function(select_by_name, string="Maturity Date", method=True, type='date'),
		'date_created': fields.function(select_by_name, string="Creation Date", method=True, type='date'),
		'ref': fields.function(select_by_name, string="Ref", method=True, type='char'),
	 }
	def onchange_move_line(self, cr, uid, id, move_line, context={}):
		if not move_line:
			return {}
		line=self.pool.get('account.move.line').browse(cr,uid,move_line)
		return {'value': {'amount': line.credit}}

payment_line()
