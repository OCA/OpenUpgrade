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

import sql_db

numerotate_form_cont = '''<?xml version="1.0"?>
<form title="%s">
	<field name="number" string="%s"/>
</form>''' % ('Continuous Numerotation','First Number')

numerotate_fields_cont = {
	'number': {'string':'First Number', 'type':'integer', 'required':True}
}

numerotate_form = '''<?xml version="1.0"?>
<form title="%s">
	<group col="1">
		<separator string="%s"/>
		<field name="lot_inv"/>
		<field name="lot_num"/>
	</group>
</form>''' % ('Catalog Numerotation','Object Reference')

numerotate_fields = {
	'lot_inv': {'string':'Depositer Inventory', 'type':'char', 'required':True},
	'lot_num': {'string':'Lot Number', 'type':'integer', 'required':True},
}

numerotate_form2 = '''<?xml version="1.0"?>
<form title="%s">
	<group>
		<separator string="%s" colspan="2"/>
		<field name="lot_inv" readonly="1"/>
		<field name="lot_num" readonly="1"/>
		<field name="name" readonly="1" colspan="3"/>
		<field name="obj_desc" readonly="1" colspan="3"/>
		<field name="lot_est1" readonly="1"/>
		<field name="lot_est2" readonly="1"/>
		<separator string="%s" colspan="2"/>
		<field name="obj_num"/>
	</group>
</form>''' % ('Catalog Numerotation','Object Reference','Object Reference')

numerotate_fields2 = {
	'lot_inv': {'string':'Object Inventory', 'type':'char', 'readonly':True},
	'lot_num': {'string':'Inventory Number', 'type':'integer', 'readonly':True},
	'lot_est1': {'string':'Minimum Estimation', 'type':'float', 'readonly':True},
	'lot_est2': {'string':'Maximum Estimation', 'type':'float', 'readonly':True},
	'name': {'string':'Short Description', 'type':'char', 'size':64, 'readonly':True},
	'obj_desc': {'string':'Description', 'type':'text', 'readonly':True},
	'obj_num': {'string':'Catalog Number', 'type':'integer', 'required':True}
}

def _read_record(self,cr,uid,datas,context={}):
	form = datas['form']
	service = netsvc.LocalService("object_proxy")
	ids = service.execute(uid, 'auction.deposit', 'search', [('name','=',form['lot_inv'])])
	res = []
	for id in ids:
		res += service.execute(uid, 'auction.lots', 'search', [('bord_vnd_id','=',id), ('lot_num','=',int(form['lot_num']))])
	found = [r for r in res if r in datas['ids']]
	if len(found)==0:
		raise wizard.except_wizard('UserError', 'This record does not exist !')
	datas = service.execute(uid, 'auction.lots', 'read', found, ['obj_num', 'name', 'lot_est1', 'lot_est2', 'obj_desc'] )
	return datas[0]

def _numerotate(self,cr,uid,datas,context={}):
	form = datas['form']
	try:
		service = netsvc.LocalService("object_proxy")
		ids = service.execute(uid, 'auction.deposit', 'search', [('name','=',form['lot_inv'])])
		if not len(ids):
			raise wizard.except_wizard('UserError', 'None object with this inventory found !')
		res = service.execute(uid, 'auction.lots', 'search', [('bord_vnd_id','=',ids[0]), ('lot_num','=',int(form['lot_num']))])
		found = [r for r in res if r in datas['ids']]
	except:
		raise wizard.except_wizard('ValidateError', ('Wrong values !', 'end'))
	if len(found)==0:
		raise wizard.except_wizard('UserError', 'None object with this inventory found !')
	try:
		service.execute(uid, 'auction.lots', 'write', found, {'obj_num':int(form['obj_num'])} )
		return {'lot_inv':'', 'lot_num':''}
	except:
		raise wizard.except_wizard('ValidateError', ('Wrong values !', 'end'))

def _numerotate_cont(self,cr,uid,datas,context={}):
	nbr = int(datas['form']['number'])
	service = netsvc.LocalService("object_proxy")
	for id in datas['ids']:
		service.execute(uid, 'auction.lots', 'write', [id], {'obj_num':nbr} )
		nbr+=1
	return {}

class wiz_auc_lots_numerotate(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch':numerotate_form, 'fields': numerotate_fields, 'state':[('search','Continue'), ('end','Exit')]}
		},
		'search': {
			'actions': [_read_record],
			'result': {'type': 'form', 'arch':numerotate_form2, 'fields': numerotate_fields2, 'state':[('set_number','Numerotation'), ('end','Exit')]}
		},
		'set_number': {
			'actions': [_numerotate],
			'result': {'type': 'state', 'state':'init'}
		}
	}
wiz_auc_lots_numerotate('auction.lots.numerotate');


class wiz_auc_lots_numerotate(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch':numerotate_form_cont, 'fields': numerotate_fields_cont, 'state':[('set_number','Numerotation'), ('end','Exit')]}
		},
		'set_number': {
			'actions': [_numerotate_cont],
			'result': {'type': 'state', 'state':'end'}
		}
	}
wiz_auc_lots_numerotate('auction.lots.numerotate_cont');


#def _set_number(self, uid, datas):
#	service = netsvc.LocalService("object_proxy")
#	res = service.execute(uid, 'auction.lots', 'numerotate', datas['ids'])
#
#class wiz_auc_lots_numerotate(wizard.interface):
#	states = {
#		'init': {
#			'actions': [_set_number],
#			'result': {'type': 'state', 'state':'end'}
#		}
#	}
#wiz_auc_lots_numerotate('auction.lots.numerotate');
