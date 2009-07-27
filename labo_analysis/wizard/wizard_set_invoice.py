##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#						  Fabien Pinckaers <fp@tiny.Be>
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
import pooler
take_form = """<?xml version="1.0"?>
<form title="Confirm">
	<separator string="Check to be invoiced" colspan="4"/>
	<newline/>
</form>
"""

take_form1 = """<?xml version="1.0"?>
<form title="Confirm">
	<separator string="Unable to be invoiced" colspan="4"/>
	<newline/>
</form>
"""

take_fields = {
#	'confirm_en': {'string':'Catalog Number', 'type':'integer'},
}

def _confirm_enable(self,cr,uid,data,context={}):
	res={}
	pool = pooler.get_pool(cr.dbname)
	pool.get('labo.sample').write(cr,uid,data['ids'],{'to_be_invoiced':False})
	return {}
def _confirm_able(self,cr,uid,data,context={}):
	res={}
	pool = pooler.get_pool(cr.dbname)
	pool.get('labo.sample').write(cr,uid,data['ids'],{'to_be_invoiced':True})
	return {}

class able_invoice(wizard.interface):
	states = {
		'init' : {
			'actions' : [],
			'result' : {
					'type' : 'form',
					'arch' : take_form,
					'fields' : take_fields,
					'state' : [('end', 'Cancel'),('go', 'Check to be Invoiced')]}
		},
			'go' : {
			'actions' : [_confirm_able],
			'result' : {'type' : 'state', 'state' : 'end'}
		},
}
able_invoice('sample.able')


class enable_invoice(wizard.interface):
	states = {
		'init' : {
			'actions' : [],
			'result' : {
					'type' : 'form',
					'arch' : take_form1,
					'fields' : take_fields,
					'state' : [('end', 'Cancel'),('go', 'Disable to be Invoiced')]}
		},
			'go' : {
			'actions' : [_confirm_enable],
			'result' : {'type' : 'state', 'state' : 'end'}
		},
}
enable_invoice('sample.enable')

