# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (c) 2008 Acysos SL. All Rights Reserved.
#    $Id$
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

import wizard
import pooler
import time

wizard_periods_form = '''<?xml version="1.0"?>
<form string="Select period">
	<field name="fiscalyear" />
	<field name="journal_id" />
	<field name="period_id" />
	<field name="date_move" />
	<field name="periods" colspan="4"/>
</form>'''

wizard_periods_fields = {
	'fiscalyear': {'string': 'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear',
		'help': 'Fiscal Year for the write move', 'required': True, },
	'journal_id': {'string': 'Journal', 'type': 'many2one', 'relation': 'account.journal', 'help': 'Journal for the move'},
	'period_id': {'string': 'Move Period', 'type': 'many2one', 'relation':'account.period', 'help': 'Period for the move', 'required': True,},
	'date_move': {'string': 'Date', 'type':'date', 'help':'Date for the move.', 'required': True,},
	'periods': {'string': 'Periods', 'type': 'many2many', 'relation': 'account.period', 'help': 'Periods to regularize', 'required':True}
}

wizard_dates_form = '''<?xml version="1.0"?>
<form string="Select period">
	<field name="fiscalyear" />
	<field name="journal_id" />
	<field name="period_id" />
	<field name="date_move" />
	<field name="date_to" colspan="2"/>
</form>'''

wizard_dates_fields = {
	'fiscalyear': {'string': 'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear',
		'help': 'Keep empty for all open fiscal year', 'required': True,},
	'journal_id': {'string': 'Journal', 'type': 'many2one', 'relation': 'account.journal', 'help': 'Journal for the move'},
	'period_id': {'string': 'Move Period', 'type': 'many2one', 'relation':'account.period', 'help': 'Period for the move', 'required': True,},
	'date_move': {'string': 'Date', 'type':'date', 'help':'Date for the move.', 'required': True,},
	'date_to': {'string': 'Date To:', 'type': 'date', 'help': 'Include movements up to this date', 'required': True,},}

class wizard_regularize(wizard.interface):

	def _init_wizard(self, cr, uid, data, context):
		regu_type = pooler.get_pool(cr.dbname).get('account.regularization').read(cr, uid, data['id'], ['balance_calc',])['balance_calc']
		if regu_type == 'date':
			return 'dates'
		return 'periods'

	def _get_default_values(self, cr, uid, data, context):
		fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
		data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
		period_obj = pooler.get_pool(cr.dbname).get('account.period')
		data['form']['period_id'] = period_obj.find(cr, uid, dt=time.strftime('%Y-%m-%d'))[0]
		data['form']['date_move'] = time.strftime('%Y-%m-%d')
		return data['form']

	def _regularize_dates(self, cr, uid, data, context):
		self._get_default_values(cr, uid, data, context)
		return data['form']

	def _regularize_periods(self, cr, uid, data, context):
		self._get_default_values(cr, uid, data, context)
		return data['form']

	def _regularize(self,cr, uid, data, context):
		regu_objs = pooler.get_pool(cr.dbname).get('account.regularization').browse(cr, uid, data['ids'])
		date = data['form']['date_move']
		period = data['form']['period_id']
		journal = data['form']['journal_id']
		date_to = None
		period_ids = []
		if 'date_to' in data['form'].keys():
			date_to = data['form']['date_to']
		if 'periods' in data['form'].keys():
			period_ids = data['form']['periods'][0][2]
		for regu in regu_objs:
			regu.regularize(context, date, period, journal, date_to, period_ids)
		return {}


	states = {
		'init': {
			'actions': [],
			'result': {'type':'choice', 'next_state':_init_wizard}
		},
		'dates': {
			'actions': [_regularize_dates],
			'result': {'type':'form', 'arch': wizard_dates_form, 'fields': wizard_dates_fields,
				'state' : (
					('end', 'Cancel'),
					('regularize', 'Regularize')
				)
			}
		},

		'periods': {
			'actions': [_regularize_periods],
			'result': {'type':'form', 'arch': wizard_periods_form, 'fields': wizard_periods_fields,
				'state' : (
					('end', 'Cancel'),
					('regularize', 'Regularize')
				)
			}
		},

		'regularize': {
			'actions': [_regularize],
			'result': {'type':'state', 'state':'end'}
		}
	}
wizard_regularize('account.regularization.regularize')


