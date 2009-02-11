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

import time
from osv import fields, osv
from base import base_delete_unit_test_records, base_get_default_currency
from decimal import Decimal

class personal_account_entry(osv.osv):
	_name = "personal.base.account.entry"
	_description = "Account Entry"
	_order = "date DESC"
	
	def _get_accounts_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		for id in ids:
			res[id] = []
			for entry in self.browse(cr, uid, [id]):
				for line in entry.line_ids:
					res[id].append([line.account_id.id])
		return res
	
	_columns = {
		'user_id': fields.many2one('res.users', 'User', required=True),
		'date': fields.date('Date', required=True, select=True, states={'confirmed':[('readonly',True)]}),
		'name': fields.char('Description', size=64, required=True, select=True, states={'confirmed':[('readonly',True)]}),
		'line_ids': fields.one2many('personal.base.account.entry.line', 'parent_id', 'Entries', states={'confirmed':[('readonly',True)]}),
		'currency_id': fields.many2one('res.currency', 'Currency', states={'confirmed':[('readonly',True)]}),
		'note': fields.text('Note'),
		'state': fields.selection([('draft', 'Draft'),('confirmed', 'Confirmed')], 'State', required=True, readonly=True),
		'created_in_model_id': fields.many2one('ir.model', 'Created in Model', required=True, readonly=True),
		
		#fields for unit_test
        'unit_test': fields.boolean(string='unit_test'),
	}
	_defaults = {
		'user_id': lambda self, cr, uid, context: uid,
		'date': lambda *a: time.strftime('%Y-%m-%d'),
		'currency_id': lambda self, cr, uid, context: base_get_default_currency(cr, uid, context),
		'created_in_model_id': lambda self, cr, uid, context: self.pool.get('ir.model').search(cr, uid, [('model','=',self._name)])[0],
		'state': lambda *a: 'draft',
		'unit_test': lambda *a: False,
	}
	
	#def test_create(self, cr, uid, vals, context={}):
	#	id = self.create(cr, user, vals, context=context)
	#	print "entry_create", vals
	#	print "entry_create", id
	
	def search(self, cr, uid, args, offset=0, limit=2000, order=None, context=None, count=False):
		args.append(('user_id','=',uid))
		for arg in args:
			if arg[0] == 'created_in_model_id':
				try:
					int(arg[2])
					created_in_model_is_string = False
				except:
					created_in_model_is_string = True
				if created_in_model_is_string:
					model_ids =	self.pool.get('ir.model').search(cr, uid,
																 [('model','=',arg[2])])
					if model_ids == []:
						raise osv.except_osv('Error', 'Unknown model %s!' % arg[2])
					arg = (arg[0], arg[1], model_ids[0])
				break
			
		return osv.orm.orm.search(self, cr, uid, args, offset, limit, order,
								  context=context)
	
	def unlink(self, cr, uid, ids, context={}, check=True):
		for entry in self.browse(cr, uid, ids, context):
			if entry.state <> 'draft':
				raise osv.except_osv('Error',
						'You can not delete confirmed entry: "%s"!' % entry.name)
			for line in entry.line_ids:
				line.unlink(cr, uid, [line.id])
		return super(personal_account_entry, self).unlink(cr, uid, ids, context)
	
	def confirm(self, cr, uid, ids, *args):
		rec_lines = self.pool.get('personal.base.account.entry.line')
		rec_currency = self.pool.get('res.currency')
		for entry in self.browse(cr, uid, ids):
			if entry.user_id.id != uid:
				raise osv.except_osv('Error', 'Wrong user!')
			if entry.state != 'draft':
				raise osv.except_osv('Error', 'Only Draft entries can be confirmed!')
			
			amount = Decimal(0)
			_debit_amount = Decimal(0)
			_credit_amount = Decimal(0)
			currency = None
			for line in entry.line_ids:
				if line.state != 'draft':
					raise osv.except_osv('Error', 'Only Draft entries can be confirmed!')
				if line.date != entry.date:
					rec_lines.write(cr, uid, [line.id], {'date': entry.date})
				
				if not currency:
					currency = line.currency_id
				if line.debit_amount != 0:
					line_amount = line.debit_amount
				else:
					line_amount =  -line.credit_amount
				
				_debit_amount += Decimal(str(rec_currency.compute_with_currency_rate(cr, uid, line.currency_id.rate, currency.id, line.debit_amount)))
				_credit_amount += Decimal(str(rec_currency.compute_with_currency_rate(cr, uid, line.currency_id.rate, currency.id, line.credit_amount)))
				amount += Decimal(str(rec_currency.compute_with_currency_rate(cr, uid, line.currency_id.rate, currency.id, line_amount)))
			
			if amount != 0:
				raise osv.except_osv('Error', 'Sum of all lines amounts must be zero! You have %s in debit and %s in credit.' % (str(_debit_amount), str(_credit_amount)))
		
		for entry in self.browse(cr, uid, ids):
			for line in entry.line_ids:
				if line.state=='draft':
					self.pool.get('personal.base.account.entry.line').write(cr, uid, [line.id], {'state':'confirmed'})
				
		self.write(cr, uid, ids, {'state':'confirmed'})
		return True
	
	def return_entry(self, cr, uid, ids, *args):
		self.write(cr, uid, ids, {'state':'draft'})
		
		for entry in self.browse(cr, uid, ids):
			for line in entry.line_ids:
				if line.state=='confirmed':
					self.pool.get('personal.base.account.entry.line').write(cr, uid, [line.id], {'state':'draft'})
		return True
	
	#for unit tests
	def delete_unit_test_records(self, cr, uid):
		user_rec = self.pool.get('res.users')
		for user in user_rec.search(cr, uid, [('unit_test','=',True)]):
			ids = self.search(cr, user, [('unit_test','=',True)])
			self.return_entry(cr, user, ids)
		base_delete_unit_test_records(self, cr, uid)
	
	def test_if_confirm_possible(self, cr, uid, ids):
		try:
			self.confirm(cr, uid, ids)
		except:
			return
		assert False, "Entries confirmation checked out not everything."
	
personal_account_entry()

class personal_account_entry_line(osv.osv):
	_name = "personal.base.account.entry.line"
	_description = "Account Entry Line"
	_order = "date, id"
	
	def _get_balance_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		for id in ids:
			line = self.browse(cr, uid, id)
			res[id] = 0.0
			for search_line_id in self.search(cr, uid, 
					[('account_id', '=', line.account_id.id),
					 ('date', '<=', line.date),
					 ('state', '=', 'confirmed')]
			):
				sum_line = self.browse(cr, uid, search_line_id)
				if (sum_line.date < line.date) or (search_line_id <= line.id):
					res[id] = res[id] + (sum_line.amount_base * line.account_id.type_id.sign)
        
#            for child_id in self.read(cr, uid, [id], ['child_ids'])[0]['child_ids']:
#                for child in self.browse(cr, uid, [child_id]):
#                    res[child_id] = child.balance
#                    res[id] = res[id] + res[child_id]
		return res
	
	def _get_amount_base_with_sign(self, cr, uid, ids, prop, unknow_none, context):
		res = {}
		for id in ids:
			line = self.browse(cr, uid, id)
			res[id] = line.amount_base * line.account_id.type_id.sign
		return res
	
	def _get_default_date(self, cr, uid, context):
		if 'date' in context:
			return context['date']
		else:
			return time.strftime('%Y-%m-%d')
	
	def _get_default_currency(self, cr, uid, context):
		if 'currency_id' in context:
			return context['currency_id']
		else:
			return 0
	
	def _check_amounts(self, cr, uid, ids):
		currency_obj = self.pool.get('res.currency')
		lines = self.browse(cr, uid, ids)
		for l in lines:
			if (l.debit_amount != 0) and (l.credit_amount != 0):
				return False

			currency_rate = currency_obj.personal_calc_currency_rate(cr, uid, l.account_id.id, l.currency_id.id)
			if (l.debit_amount != 0):
				local_amount_base = self._calc_amount_base(cr, uid, l.account_id.id, currency_rate, l.debit_amount)
			else:
				local_amount_base = self._calc_amount_base(cr, uid, l.account_id.id, currency_rate, -l.credit_amount)
			
			hasChanges = False
			if (currency_obj.round(cr, uid, l.currency_id, l.amount_base) != currency_obj.round(cr, uid, l.currency_id, local_amount_base)):
				self.write(cr, uid, [l['id']], {'amount_base': local_amount_base})
		return True
	
	_columns = {
		'user_id': fields.many2one('res.users', 'User', required=True),
	    'date': fields.date('Date', required=True, states={'confirmed':[('readonly',True)]}),
		'parent_id': fields.many2one('personal.base.account.entry', 'Entry', required=True, states={'confirmed':[('readonly',True)]}),
		'name': fields.char('Description', size=64, select=True, states={'confirmed':[('readonly',True)]}),
		'account_id': fields.many2one('personal.base.account', 'Account', required=True, select=True, states={'confirmed':[('readonly',True)]}),
		'currency_id': fields.many2one('res.currency', 'Currency', required=True, states={'confirmed':[('readonly',True)]}),
		'currency_rate': fields.float('Currency Rate', digits=(12,6), required=True, states={'confirmed':[('readonly',True)]}),
		'debit_amount': fields.float('Debit Amount', digits=(10,2), states={'confirmed':[('readonly',True)]}),
		'credit_amount': fields.float('Credit Amount', digits=(10,2), states={'confirmed':[('readonly',True)]}),
		#'amount': fields.float('Amount', digits=(10,2)),
		'amount_base': fields.float('Amount Base', digits=(10,2), states={'confirmed':[('readonly',True)]}),
		'state': fields.selection([('draft', 'Draft'),('confirmed', 'Confirmed')], 'State', required=True, readonly=True),

		'balance': fields.function(_get_balance_fnc, method=True, type="float", digits=(10,2), string='Balance'),
		'amount_base_with_sign': fields.function(_get_amount_base_with_sign, method=True, type="float", digits=(10,2), string='Amount'),
		
		#fields for unit_test
        'unit_test': fields.boolean(string='unit_test')
	}
	_defaults = {
		'user_id': lambda self, cr, uid, context: uid,
		'date': lambda self, cr, uid, context: \
				self._get_default_date(cr, uid, context=context),
		'currency_id': lambda self, cr, uid, context: \
				self._get_default_currency(cr, uid, context=context),
		'currency_rate': lambda *a: 1,
		'state': lambda *a: 'draft',
		
		'unit_test': lambda *a: False,
	}
	_constraints = [
        (_check_amounts, 'Error: You must enter only one amount.', ['debit_amount', 'credit_amount'])
    ]	
	_fields_from_parent = ['date', 'currency_id']
	
	def create(self, cr, uid, vals, context={}):
		#without this don't work 'parent_id' in unit tests
		if ("unit_test" in vals) and (vals["unit_test"]):	
			cr.commit()
		
		entry_rec = self.pool.get('personal.base.account.entry')
		parent = entry_rec.read(cr, uid, [vals['parent_id']], self._fields_from_parent)
		for field in self._fields_from_parent:
			if not (field in context): 
				if parent[0][field]:
					if ('_id' in field):
						field_value = parent[0][field][0]
					else:
						field_value = parent[0][field]
				if not (field in vals):
					context[field] = field_value
				else:
					context[field] = field_value
					
		#needed for unit test, because <record> tag haven't uid attribute
		user = uid
		if ('user_id' in vals) and (vals['user_id'] != user):
			user = vals['user_id']
		
		if ("account_id" in vals):
			acc_rec = self.pool.get('personal.base.account')
			if acc_rec.read(cr, user, [vals["account_id"]], ['user_id'])[0]['user_id'][0] != user:
				raise osv.except_osv('Error', 'Wrong account!')
		if ("parent_id" in vals):
			if entry_rec.read(cr, user, [vals["parent_id"]], ['user_id'])[0]['user_id'][0] != user:
				raise osv.except_osv('Error', 'Wrong entry line parent!')
				
		return super(personal_account_entry_line, self).create(cr, user, vals, context=context)
	
	def search(self, cr, uid, args, offset=0, limit=2000, order=None, context=None, count=False):
		args.append(('user_id','=',uid))
		if context:
			if 'filter_by_active_id' in context:
				args.append(('parent_id','=',
					self.read(cr, uid, [context['filter_by_active_id']], ['parent_id'])['parent_id'][0]))
		return osv.orm.orm.search(self, cr, uid, args, offset, limit, order,
								  context=context)
		
	def confirm(self, cr, uid, ids):
		for line in self.browse(cr, uid, ids):
			if ((line.debit_amount == 0) and (line.credit_amount == 0)) or (line.amount_base == 0):
				raise osv.except_osv('Error', 'Not found line amount!')
		
		self.write(cr, uid, ids, {'state':'confirmed'})
	
	def unlink(self, cr, uid, ids, context={}, check=True):
		for line in self.browse(cr, uid, ids, context):
			if line.state <> 'draft':
				raise osv.except_osv('Error', 'You can not delete confirmed entry: "%s"!' % (line.name or ''))
		return super(personal_account_entry_line, self).unlink(cr, uid, ids, context)
	
	
	
	def return_entry(self, cr, uid, ids):
		self.write(cr, uid, ids, {'state':'draft'})
	
	def _calc_amount_base(self, cr, uid, account_id, currency_rate, amount):
		if not account_id:
			return amount
		
		acc_pool = self.pool.get('personal.base.account')
		currency_pool = self.pool.get('res.currency')
		
		account = acc_pool.browse(cr, uid, account_id)
		to_currency = account.currency_id.id
		if currency_rate != 1:
			return currency_pool.compute_with_currency_rate(cr, uid, currency_rate, to_currency, amount)
		else:
			return amount
		#line_rec = self.pool.get('personal.base.account.entry.line')
		#acc_rec = self.pool.get('personal.base.account')
		#currency_rec = self.pool.get('res.currency')
		#for id in ids:
		#	curr_line = self.read(cr, uid, [id], ["amount", "account_id", "currency_id"])[0]
		#	curr_acc = acc_rec.read(cr, uid, [curr_line["account_id"][0]], ["currency_id"])[0]
		#	from_currency = curr_line["currency_id"][0]
		#	to_currency = curr_acc["currency_id"][0]
		#	if from_currency != to_currency:
		#		self.write(cr, uid, id, 
		#			{'amount_base': currency_rec.compute(cr, uid, from_currency, to_currency, curr_line["amount"])})
		#	else:
		#		self.write(cr, uid, id, 
		#			{'amount_base': currency_rec.compute(cr, uid, from_currency, to_currency, curr_line["amount"])})
	
	def onchange_base(self, cr, uid, ids, state):
		if state == 'confirmed':
			raise osv.except_osv('Error', 'It is not allowed to edit confirmed entries!')
		
		return {'value':{}}

	def onchange_debit_amount(self, cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state):
		debit_amount -= credit_amount
		credit_amount = 0
		return self.onchange_amount(cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state)
	
	def onchange_credit_amount(self, cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state):
		credit_amount += debit_amount
		debit_amount = 0
		return self.onchange_amount(cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state)
	
	#This is allways the last onchange function
	def onchange_amount(self, cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state):
		self.onchange_base(cr, uid, ids, state)
		
		v = {'value':{}}
		if debit_amount>0:
			_amount = debit_amount
		else:
			_amount = -credit_amount
		v['value']['currency_id'] = currency_id
		v['value']['currency_rate'] = currency_rate
		v['value']['credit_amount'] = credit_amount
		v['value']['debit_amount'] = debit_amount
		v['value']['amount_base'] = self._calc_amount_base(cr, uid, account_id, currency_rate, _amount)
		return v
	
	def onchange_currency_id(self, cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state):
		self.onchange_base(cr, uid, ids, state)
		
		currency_pool = self.pool.get('res.currency')
		currency_rate = currency_pool.personal_calc_currency_rate(cr, uid, account_id, currency_id)
		return self.onchange_amount(cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state)
	
	def onchange_account_id(self, cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state):
		self.onchange_base(cr, uid, ids, state)
		
		#v = {'value':{}}
		if (account_id and (not currency_id or not currency_rate)):
			acc_pool = self.pool.get('personal.base.account')
			account = acc_pool.browse(cr, uid, account_id)
			currency_id = account.currency_id.id
		return self.onchange_currency_id(cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state)
	
	def onchange_amount_base(self, cr, uid, ids, account_id, currency_id, currency_rate, amount_base, state):
		self.onchange_base(cr, uid, ids, state)
		
		currency_pool = self.pool.get('res.currency')
		currency_rate = currency_pool.personal_calc_currency_rate(cr, uid, account_id, currency_id)
		debit_amount = 0
		credit_amount = 0
		if currency_rate != 0:
			if amount_base > 0:
				debit_amount = amount_base / currency_rate
			else:
				credit_amount = (-amount_base) / currency_rate
		else:
			amount_base = 0
		return self.onchange_amount(cr, uid, ids, account_id, currency_id, currency_rate, debit_amount, credit_amount, state)
	
	#for unit tests
	def delete_unit_test_records(self, cr, uid):
		base_delete_unit_test_records(self, cr, uid)
	
	def test_if_create_is_impossible(self, cr, uid, collumns):
		#if not ('parent_id' in collumns):
		#	return
		#parent = self.pool.get('personal.base.account.entry').read(cr, uid, collumns['parent_id'], ['date', 'currency_id'])
		try:
			new_id = self.create(cr, uid, collumns)
		except:
			cr.commit()
			return
		self.unlink(cr, uid, [new_id])
		assert False, "Entry Lines creation checked out not everything."
	
personal_account_entry_line()
