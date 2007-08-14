# -*- coding: iso-8859-1 -*-
##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
import netsvc

close_form = '''<?xml version="1.0"?>
<form title="Paid ?">
	<field name="adj"/>
	<newline/>
	<field name="frais"/>
	<newline/>
	<field name="total"/>
	<newline/>
	<field name="salle"/>
	<newline/>
	<field name="voirie"/>
	<newline/>
	<field name="acquis"/>
</form>'''

close_fields = {
	'adj': {'string':'Adjudications', 'type':'float', 'digits':(14,2), 'readonly':True},
	'frais': {'string':'Frais de vente', 'type':'float', 'digits':(12,2), 'readonly':True},
	'total': {'string':'Total', 'type':'float', 'digits':(12,2), 'readonly':True},
	'salle': {'string':'Frais de salle', 'type':'float', 'digits':(12,2), 'readonly':True},
	'voirie': {'string':'Frais de voirie', 'type':'float', 'digits':(12,2)},
	'acquis': {'string':'Pour acquis', 'type':'boolean'}
}

wait_form = '''<?xml version="1.0"?>
<form title="Waiting for PV">
</form>'''

class wizard_close_dossier(wizard.interface):
	def _get_value(self, uid, datas):
		service = netsvc.LocalService("object_proxy")

		res = service.execute(uid, 'huissier.dossier', 'read', datas['ids'], ['amount_adj_calculated','amount_costs','amount_total','amount_room_costs'])
		return len(res) and {'adj':res[0]['amount_adj_calculated'], 'frais':res[0]['amount_costs'], 'total':res[0]['amount_total'], 'salle':res[0]['amount_room_costs']} or {}

	def _close_dossier(self, uid, datas):
		service = netsvc.LocalService("object_proxy")
		res = service.execute(uid, 'huissier.dossier', 'close', datas['ids'], datas['form']['voirie'], datas['form']['acquis'])
		return {'refund_id':res[0], 'invoice_id':res[1]}
		
	def _get_invoice_id(self, uid, datas):
		return {'ids': [datas['form']['invoice_id']]}
	
	def _check_invoice(self, uid, datas):
		return datas['form']['invoice_id'] and 'wait_pv' or 'end'
		
	def _check_refund(self, uid, datas):
		return datas['form']['refund_id'] and 'wait_invoice' or 'end'
		
	def _get_refund_id(self, uid, datas):
		return {'ids': [datas['form']['refund_id']]}
		
	states = {
		'init': {
			'actions': [_get_value], 
			'result': {'type':'form', 'arch':close_form, 'fields':close_fields, 'state':[('close_dossier','Cloturer le PV'), ('end','Annuler')]}
		},
		'close_dossier': {
			'actions': [_close_dossier],
			'result': {'type':'print', 'report':'huissier.pv', 'state':'check_invoice'}
		},
		'check_invoice': {
			'actions': [],
			'result': {'type':'choice', 'next_state':_check_invoice}
		},
		'wait_pv': {
			'actions': [],
			'result': {'type':'form', 'arch':wait_form, 'fields':{}, 'state':[('print_invoice','Imprimer la facture'), ('end','Fermer')]}
		},
		'print_invoice': {
			'actions': [_get_invoice_id],
			'result': {'type':'print', 'report':'account.invoice', 'get_id_from_action':True, 'state':'check_refund'}
		},
		'check_refund': {
			'actions': [],
			'result': {'type':'choice', 'next_state':_check_refund}
		},
		'wait_invoice': {
			'actions': [],
			'result': {'type':'form', 'arch':wait_form, 'fields':{}, 'state':[('print_refund',u'Imprimer la note de crédit'), ('end','Fermer')]}
		},
		'print_refund': {
			'actions': [_get_refund_id],
			'result': {'type':'print', 'report':'account.invoice', 'get_id_from_action':True, 'state':'end'}
		}
	}
wizard_close_dossier('huissier.dossier.close')

class wizard_close_dossier_from_lot(wizard_close_dossier):
	def _get_value(self, uid, datas,context={}):
		service = netsvc.LocalService("object_proxy")

		# get the dossier from the first lot
		lots = service.execute(uid, 'huissier.lots', 'read', [datas['ids'][0]], ['dossier_id'])
		dossier_id = lots and lots[0]['dossier_id'][0] or False
		dossier_ids = dossier_id and [dossier_id] or []
#TODO: error si dossier déjà fermé? le prob c'est il faut pouvoir corriger une erreur...
		res = service.execute(uid, 'huissier.dossier', 'read', dossier_ids, ['amount_adj_calculated','amount_costs','amount_total','amount_room_costs'])
		return res and {'dossier_id':dossier_id, 'adj':res[0]['amount_adj_calculated'], 'frais':res[0]['amount_costs'], 'total':res[0]['amount_total'], 'salle':res[0]['amount_room_costs']} or {'dossier_id':dossier_id}

	def _close_dossier(self, uid, datas):
		service = netsvc.LocalService("object_proxy")
		
		res = service.execute(uid, 'huissier.dossier', 'close', [datas['form']['dossier_id']], datas['form']['voirie'], datas['form']['acquis'])
		return {'ids':[datas['form']['dossier_id']], 'refund_id':res[0], 'invoice_id':res[1]}

	states = {
		'init': {
			'actions': [_get_value], 
			'result': {'type':'form', 'arch':close_form, 'fields':close_fields, 'state':[('close_dossier','Cloturer le PV'), ('end','Annuler')]}
		},
		'close_dossier': {
			'actions': [_close_dossier],
			'result': {'type':'print', 'report':'huissier.pv', 'get_id_from_action':True, 'state':'check_invoice'}
		},
		'check_invoice': {
			'actions': [],
			'result': {'type':'choice', 'next_state':wizard_close_dossier._check_invoice}
		},
		'wait_pv': {
			'actions': [],
			'result': {'type':'form', 'arch':wait_form, 'fields':{}, 'state':[('print_invoice','Imprimer la facture'), ('end','Fermer')]}
		},
		'print_invoice': {
			'actions': [wizard_close_dossier._get_invoice_id],
			'result': {'type':'print', 'report':'account.invoice', 'get_id_from_action':True, 'state':'check_refund'}
		},
		'check_refund': {
			'actions': [],
			'result': {'type':'choice', 'next_state':wizard_close_dossier._check_refund}
		},
		'wait_invoice': {
			'actions': [],
			'result': {'type':'form', 'arch':wait_form, 'fields':{}, 'state':[('print_refund',u'Imprimer la note de crédit'), ('end','Fermer')]}
		},
		'print_refund': {
			'actions': [wizard_close_dossier._get_refund_id],
			'result': {'type':'print', 'report':'account.invoice', 'get_id_from_action':True, 'state':'end'}
		}
	}
wizard_close_dossier_from_lot('huissier.dossier.close.from_lot')

