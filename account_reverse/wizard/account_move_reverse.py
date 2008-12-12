##############################################################################
#
# Copyright (c) 2008 ACYSOS S.L. (http://acysos.com) All Rights Reserved.
#
# $Id$
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


