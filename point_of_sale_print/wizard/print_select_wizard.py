# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2009 P. Christeas. All Rights Reserved
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
# import time
# import datetime
import pooler
from tools.translate import _

# This code is a dirty hack around the openerp base modules, so that 
# a pos print can be carried without interfering with the core ir_actions
# classes. Ideally, the ir.actions.report.postxt should behave like all
# other actions.

select_form = """<?xml version="1.0"?>
<form string="Select print">
    <field name="pos_action_id"/>
</form>
"""

select_fields = {
	'pos_action_id': {'relation':'ir.actions.report.postxt', 'type': 'many2one',
		'string':'Report', 'required':True },
	}

def _pos_print(self, cr, uid, data, context):
    #wf_service = netsvc.LocalService('workflow')
    pool = pooler.get_pool(cr.dbname)
    # print "Data:",  data['form']['pos_action_id']
    pos_pobj = pool.get('ir.actions.report.postxt')
    pos_print = pos_pobj.read(cr,uid,data['form']['pos_action_id'], [])
    # print "print:", pos_print
    if pos_print['model'] != data['model']:
	raise wizard.except_wizard(_('UserError'), _('Incorrect report for this model !'))
    
    mod_obj = pool.get(data['model'])
    mobjs= mod_obj.read(cr,uid,data['ids'])
    
    for obj in mobjs:
    	pos_pobj.pprint(cr,uid,pos_print, obj, context)
    return {}

class wizard_report(wizard.interface):

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':select_form, 'fields':select_fields, 
	    	'state':[('end','Cancel'),('print','Print')]},
        },
        'print': {
            'actions': [_pos_print],
            'result': {'type':'state' , 'state':'end'},
        },
    }

wizard_report('wizard.point_of_sale_print.print')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
