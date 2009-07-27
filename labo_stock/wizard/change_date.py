#############################################################################
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

import time
import wizard
import netsvc
import pooler
from osv.orm import browse_record
import sql_db
new_date_form = """<?xml version="1.0"?>
<form string="Assign a new expiry date">
<notebook>
<page string="">
<field name="old_date"/>
<field name="new_date"/>
</page>
</notebook>
</form>
"""
new_date_fields={
		'old_date': {'string':'Current date', 'type':'date', 'relation':''},
		'new_date': {'string':'New expiry Date', 'type':'date', 'relation':''},
}

def _values(self,cr,uid,data,context):
	pool = pooler.get_pool(cr.dbname)
	rec=pool.get('stock.reactives').browse(cr,uid,data['id'],context)
	dat_n= rec and rec.exp_date2 or False
	return {'old_date':dat_n}


def _change_date(self, cr, uid, data, context):
	react_id = pooler.get_pool(cr.dbname).get('stock.reactives')
	for rec in react_id.browse(cr,uid,data['ids']):
		new_id=pooler.get_pool(cr.dbname).get('reactive.history').create(cr,uid,{
											'reactive_id':rec.id,
											'name': rec.exp_date2})
		up_react=pooler.get_pool(cr.dbname).get('stock.reactives').write(cr,uid,[rec.id],{'exp_date2':data['form']['new_date']})
	return {}




class wizard_change_date(wizard.interface):
	 states = {
		  'init' : {
				'actions' : [_values],
				'result' : {'type' : 'form',
						'arch' : new_date_form,
						'fields' :new_date_fields,
						'state' : [('end', 'Cancel'), ('change', 'Change')]}
		},
		'change' : {
				'actions' : [_change_date],
				'result' : {'type' : 'state','state' : 'end'}
		},
	 }
wizard_change_date('expired.changes')
