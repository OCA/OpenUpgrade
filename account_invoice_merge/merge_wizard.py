# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2009 P. Christeas. All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 of the License.
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
import wizard
# import time
# import datetime
import pooler
from tools.translate import _
from tools.misc import UpdateableStr, UpdateableDict

# This code is a dirty hack around the openerp base modules, so that 
# a pos print can be carried without interfering with the core ir_actions
# classes. Ideally, the ir.actions.report.postxt should behave like all
# other actions.

_confirm_form = UpdateableStr("""<?xml version="1.0"?>
<form string="%s">
    <label string="%s" colspan="4" />
</form>
""" %(_("Merge Invoices"), _("Do you really want to merge the invoices?")))

# 2go
_select_fields = UpdateableDict({
	'pos_action_ids': {'type': 'many2many',
		'string':_('Labels'), 'required':True, 'relation': 'ir.actions.report.postxt', 
		'domain': []},
	'copies': {'type': 'integer',
		'string':_('Number of copies'), 'required':False, 'help': _('Number of copies for each kind of labels. If left blank, default number will be used') },
	})
#------

def _dirty_check(self, cr, uid, data, context):
	if (len(data['ids'])<2):
		raise wizard.except_wizard(_('UserError'), _('No need to merge less than 2 invoices!'))
	pool = pooler.get_pool(cr.dbname)
	inv_obj = pool.get('account.invoice')
	invs = inv_obj.read(cr,uid,data['ids'],['account_id','state','type', 'company_id',
		'partner_id','currency_id','journal_id'])
	for d in invs:
		if d['state'] != 'draft':
			raise wizard.except_wizard(_('UserError'), _('At least one of the selected invoices is %s!')%d['state'])
		if (d['account_id'] != invs[0]['account_id']):
			raise wizard.except_wizard(_('UserError'), _('Not all invoices use the same account!'))
		if (d['company_id'] != invs[0]['company_id']):
			raise wizard.except_wizard(_('UserError'), _('Not all invoices are at the same company!'))
		if (d['partner_id'] != invs[0]['partner_id']):
			raise wizard.except_wizard(_('UserError'), _('Not all invoices are for the same partner!'))
		if (d['type'] != invs[0]['type']):
			raise wizard.except_wizard(_('UserError'), _('Not all invoices are of the same type!'))
		if (d['currency_id'] != invs[0]['currency_id']):
			raise wizard.except_wizard(_('UserError'), _('Not all invoices are at the same currency!'))
		if (d['journal_id'] != invs[0]['journal_id']):
			raise wizard.except_wizard(_('UserError'), _('Not all invoices are at the same journal!'))

	return {}


def _invoice_merge(self, cr, uid, data, context):
	if (len(data['ids'])<2):
		raise wizard.except_wizard(_('UserError'), _('No need to merge less than 2 invoices!'))
	pool = pooler.get_pool(cr.dbname)
	inv_obj = pool.get('account.invoice')
	invs = inv_obj.read(cr,uid,data['ids'])
	vals = {}
	inv_ids = []
	
	for d in invs[1:]:
		inv_ids.append(d['id'])
		if d['comment']:
			if not vals.has_key('comment'):
				vals['comment'] = invs[0]['comment'] or ''
			vals['comment']+= ' '+ d['comment']
		if d['date_due']:
			if not vals.has_key('date_due'):
				vals['date_due'] = invs[0]['date_due']
			if vals['date_due'] and (vals['date_due'] > d['date_due']):
				vals['date_due'] = d['date_due']
				
	#Now, alter all invoice lines and tax lines that pointed to merged invoices
	ilobj = pool.get('account.invoice.line')
	mlines = ilobj.search(cr,uid,[('invoice_id','in',inv_ids)])
	ilobj.write(cr,uid,mlines,{'invoice_id': invs[0]['id']})

	itobj = pool.get('account.invoice.tax')
	tlines = itobj.search(cr,uid,[('invoice_id','in',inv_ids)])
	itobj.write(cr,uid,tlines,{'invoice_id': invs[0]['id']})

	# Finally, remove merged invoices
	inv_obj.unlink(cr,uid,inv_ids)

	inv_obj.button_compute(cr,uid,[invs[0]['id'],])
	return {}



class wizard_merge(wizard.interface):

    states = {
        'init': {
            'actions': [ _dirty_check],
            'result': {'type':'form', 'arch': _confirm_form, 
		'fields': {},
	    'state':[('end','Abort'),('merge','Merge')]},
        },
        'merge': {
            'actions': [_invoice_merge],
            'result': {'type':'state' , 'state':'end'},
        },
    }

wizard_merge('account.invoice.merge.wizard')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
