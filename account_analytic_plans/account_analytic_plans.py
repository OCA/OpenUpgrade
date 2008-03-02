# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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
from xml import dom

from mx import DateTime
from mx.DateTime import now
import time

import netsvc
from osv import fields, osv,orm
import ir

import tools

class one2many_mod2(fields.one2many):
	def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
		if not context:
			context = {}
		res = {}
		for id in ids:
			res[id] = []
		ids2 = None
		if 'journal_id' in context:
			journal = obj.pool.get('account.journal').browse(cr, user, context['journal_id'], context)
			pnum = int(name[7]) -1
			plan = journal.plan_id
			if plan and len(plan.plan_ids)>pnum:
				acc_id = plan.plan_ids[pnum].root_analytic_id.id
				ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',ids),('analytic_account_id','child_of',[acc_id])], limit=self._limit)
		if ids2 is None:
			ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',ids)], limit=self._limit)
		for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
			res[r[self._fields_id]].append( r['id'] )
		return res

class account_analytic_plan(osv.osv):
	_name = "account.analytic.plan"
	_description = "Analytic Plans"
	_columns = {
		'name': fields.char('Analytic Plan', size=64, required=True, select=True,),
		'plan_ids': fields.one2many('account.analytic.plan.line','plan_id','Analytic Plans'),
	}
account_analytic_plan()

class account_analytic_plan_line(osv.osv):
	_name = "account.analytic.plan.line"
	_description = "Analytic Plan Lines"
	_columns = {
		'plan_id':fields.many2one('account.analytic.plan','Analytic Plan'),
		'name': fields.char('Plan Name', size=64, required=True, select=True),
		'sequence':fields.integer('Sequence'),
		'root_analytic_id': fields.many2one('account.analytic.account','Root Account',help="Root account of this plan.",required=True),
	}
	_order = "sequence,id"
account_analytic_plan_line()

class account_analytic_plan_instance(osv.osv):
	_name='account.analytic.plan.instance'
	_description = 'Object for create analytic entries from invoice lines'
	_columns={
		'name':fields.char('Analytic Distribution',size=64),
		'code':fields.char('Distribution Code',size=16),
		'journal_id': fields.many2one('account.analytic.journal', 'Analytic Journal', required=True),
		'account_ids':fields.one2many('account.analytic.plan.instance.line','plan_id','Account Id'),
		'account1_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account1 Id'),
		'account2_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account2 Id'),
		'account3_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account3 Id'),
		'account4_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account4 Id'),
		'account5_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account5 Id'),
		'account6_ids':one2many_mod2('account.analytic.plan.instance.line','plan_id','Account6 Id'),
		'plan_id':fields.many2one('account.analytic.plan', "Model's Plan"),
	}
	def copy(self, cr, uid, id, default=None, context=None):
		if not default:
			default = {}
			default.update({'account1_ids':False, 'account2_ids':False, 'account3_ids':False, 
				'account4_ids':False, 'account5_ids':False, 'account6_ids':False})
		return super(account_analytic_plan_instance, self).copy(cr, uid, id, default, context)

	_defaults = {
		'plan_id': lambda *args: False,
	}
	def name_get(self, cr, uid, ids, context={}):
		res = []
		for inst in self.browse(cr, uid, ids, context):
			name = inst.name or ''
			if name and inst.code:
				name=name+' ('+inst.code+')'
			res.append((inst.id, name))
		return res

	def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
		args= args or []
		if name:
			ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context or {})
			if not ids:
				ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context or {})
		else:
			ids = self.search(cr, uid, args, limit=limit, context=context or {})
		return self.name_get(cr, uid, ids, context or {})

	def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False):
		wiz_id = self.pool.get('ir.actions.wizard').search(cr, uid, [("wiz_name","=","create.model")])
		res = super(account_analytic_plan_instance,self).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
		if (res['type']=='form'):
			plan_id = False
			if context.get('journal_id',False):
				plan_id = self.pool.get('account.journal').browse(cr, uid, int(context['journal_id']), context).plan_id
			elif context.get('plan_id',False):
				plan_id = self.pool.get('account.analytic.plan').browse(cr, uid, int(context['plan_id']), context).plan_id
			if plan_id:
				i=1
				res['arch'] = """<form string="%s">
	<field name="name"/>
	<field name="code"/>
	<field name="journal_id"/>
	<button name="%d" string="Save This Distribution as a Model" type="action" colspan="2"/>
	"""% (tools.to_xml(plan_id.name), wiz_id[0])
				for line in plan_id.plan_ids:
					res['arch']+="""
					<field name="account%d_ids" string="%s" colspan="4">
					<tree string="%s" editable="bottom">
						<field name="rate"/>
						<field name="analytic_account_id" domain="[('parent_id','child_of',[%d])]"/>
					</tree>
				</field>
				<newline/>"""%(i,tools.to_xml(line.name),tools.to_xml(line.name),line.root_analytic_id and line.root_analytic_id.id or 0)
					i+=1
				res['arch'] += "</form>"
				doc = dom.minidom.parseString(res['arch'])
				xarch, xfields = self._orm__view_look_dom_arch(cr, uid, doc, context=context)
				res['arch'] = xarch
				res['fields'] = xfields
			return res
		else:
			return res
	def write(self, cr, uid, ids, vals, context={}, check=True, update_check=True):
		if context.get('journal_id',False):
			new_copy=self.copy(cr, uid, ids[0], context=context)
			vals['plan_id']=False
		return super(account_analytic_plan_instance, self).write(cr, uid, ids, vals, context)
account_analytic_plan_instance()

class account_analytic_plan_instance_line(osv.osv):
	_name='account.analytic.plan.instance.line'
	_description = 'Object for create analytic entries from invoice lines'
	_columns={
		'plan_id':fields.many2one('account.analytic.plan.instance','Plan Id'),
		'analytic_account_id':fields.many2one('account.analytic.account','Analytic Account'),
		'rate':fields.float('Rate (%)'),
	}
	def name_get(self, cr, uid, ids, context={}):
		if not len(ids):
			return []
		reads = self.read(cr, uid, ids, ['analytic_account_id'], context)
		res = []
		for record in reads:
			res.append((record['id'], record['analytic_account_id']))
		return res

account_analytic_plan_instance_line()

class account_journal(osv.osv):
	_inherit='account.journal'
	_name='account.journal'
	_columns = {
		'plan_id':fields.many2one('account.analytic.plan','Analytic Plans'),
	}
account_journal()

class account_invoice_line(osv.osv):
	_inherit='account.invoice.line'
	_name='account.invoice.line'
	_columns = {
		'analytics_id':fields.many2one('account.analytic.plan.instance','Analytic Distribution'),
	}
	def move_line_get_item(self, cr, uid, line, context={}):
		res= super(account_invoice_line,self).move_line_get_item(cr, uid, line, context={})
		res ['analytics_id']=line.analytics_id.id
		return res
account_invoice_line()

class account_move_line(osv.osv):
	_inherit='account.move.line'
	_name='account.move.line'
	_columns = {
		'analytics_id':fields.many2one('account.analytic.plan.instance','Analytic Distribution'),
	}
	def _analytic_update(self, cr, uid, ids, context):
		for line in self.browse(cr, uid, ids, context):
			if line.analytics_id:
				toremove = self.pool.get('account.analytic.line').search(cr, uid, [('move_id','=',line.id)], context=context)
				if toremove:
					self.pool.get('account.analytic.line').unlink(cr, uid, toremove, context=context)
				for line2 in line.analytics_id.account_ids:
					val = (line.debit or 0.0) - (line.credit or  0.0)
					amt=val * (line2.rate/100)
					al_vals={
						'name': line.name,
						'date': line.date,
						'account_id': line2.analytic_account_id.id,
						'amount': amt,
						'general_account_id': line.account_id.id,
						'move_id': line.id,
						'journal_id': line.analytics_id.journal_id.id,
						'ref': line.ref,
					}
					ali_id=self.pool.get('account.analytic.line').create(cr,uid,al_vals)
		return True

	def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
		result = super(account_move_line, self).write(cr, uid, ids, vals, context, check, update_check)
		self._analytic_update(cr, uid, ids, context)
		return result

	def create(self, cr, uid, vals, context=None, check=True):
		result = super(account_move_line, self).create(cr, uid, vals, context, check)
		self._analytic_update(cr, uid, [result], context)
		return result
account_move_line()

class account_invoice(osv.osv):
	_name = "account.invoice"
	_inherit="account.invoice"
	def line_get_convert(self, cr, uid, x, part, date, context={}):
		res=super(account_invoice,self).line_get_convert(cr, uid, x, part, date, context)
		res['analytics_id']=x.get('analytics_id',False)
		return res
account_invoice()

class account_analytic_plan(osv.osv):
	_inherit = "account.analytic.plan"
	_columns = {
		'default_instance_id': fields.many2one('account.analytic.plan.instance', 'Default Entries'),
	}
account_analytic_plan()


