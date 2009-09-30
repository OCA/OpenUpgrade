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

wizard_form = '''<?xml version="1.0"?>
<form string="Select period and date">
	<field name="journal_id" />
	<field name="period_id" />
	<field name="date" />
	<field name="reconcile" />
	<field name="repeat_param"/>
</form>'''

wizard_fields = {
	'journal_id': {'string': 'Journal', 'type': 'many2one', 'relation':'account.journal', 'help': 'Journal for the reversion move', 'required': True,},
	'period_id': {'string': 'Move Period', 'type': 'many2one', 'relation':'account.period', 'help': 'Period for the reversion move', 'required': True,},
	'date': {'string': 'Date', 'type':'date', 'help':'Date for the move.', 'required': True,},
	'reconcile' : { 'string': 'Reconcile', 'type': 'boolean', 'help': 'Reconcile Moves?', },
       'repeat_param' : { 'string': 'Repeat params', 'type': 'boolean', 'help': 'Reverse each move on the same date and period as the original move', }
}

class wizard_move_reverse(wizard.interface):

	def _get_default_values(self, cr, uid, data, context):
		first_move_obj = pooler.get_pool(cr.dbname).get('account.move').browse(cr, uid, data['id'])
		data['form']['journal_id'] = first_move_obj.journal_id.id
		data['form']['period_id'] = first_move_obj.period_id.id
		data['form']['date'] = first_move_obj.date
		data['form']['reconcile'] = True
		data['form']['repeat_param'] = True
		return data['form']

	def _reverse_moves(self, cr, uid, data, context):
		self._get_default_values(cr, uid, data, context)
		return data['form']


	def _reverse(self,cr, uid, data, context):
		move_objs = pooler.get_pool(cr.dbname).get('account.move').browse(cr, uid, data['ids'])
		journal = data['form']['repeat_param'] and data['form']['journal_id']
		date = data['form']['repeat_param'] and data['form']['date']
		period = data['form']['repeat_param'] and data['form']['period_id']
		reconcile = data['form']['reconcile']
		for move in move_objs:
			move.revert_move(journal, period, date, reconcile)
		return {}


	states = {
		'init': {
			'actions': [_reverse_moves],
			'result': {'type':'form', 'arch': wizard_form, 'fields': wizard_fields,
				'state' : (
					('end', 'Cancel'),
					('reverse', 'Reverse')
				)
			}
		},

		'reverse': {
			'actions': [_reverse],
			'result': {'type':'state', 'state':'end'}
		}
	}
wizard_move_reverse('account.move.reverse')


