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

_select_form = UpdateableStr("""<?xml version="1.0"?>
<form string="%s">
    <label string="%s" colspan="4" />
    <field name="pos_action_ids" colspan="4"/>
    <field name="copies"/>
</form>
""" %( _("Select print"), _("Select labels to print")))

_select_fields = UpdateableDict({
	'pos_action_ids': {'type': 'many2many',
		'string':_('Labels'), 'required':True, 'relation': 'ir.actions.report.postxt', 
		'domain': []},
	'copies': {'type': 'integer',
		'string':_('Number of copies'), 'required':False, 'help': _('Number of copies for each kind of labels. If left blank, default number will be used') },
	})

def _update_wizard(self, cr, uid, data, context):
	_select_fields['pos_action_ids']['domain'] = [ ('model','=',data['model'])]
	return {}


def _pos_print(self, cr, uid, data, context):
    #wf_service = netsvc.LocalService('workflow')
    pool = pooler.get_pool(cr.dbname)
    pos_ids=data['form']['pos_action_ids'][0][2]
    pos_pobj = pool.get('ir.actions.report.postxt')
    if not len(pos_ids):
        raise wizard.except_wizard(_('No report found'), _('Cannot locate the reports') )
    #print "pos_id:", pos_id
    pos_prints = pos_pobj.read(cr,uid,pos_ids, [])
    # print "print:", pos_print
    
    if data['form']['copies']:
	for pobj in pos_prints:
		pobj['copies'] = data['form']['copies']
    mod_obj = pool.get(data['model'])
    mobjs= mod_obj.read(cr,uid,data['ids'])
    
    for obj in mobjs:
	for pobj in pos_prints:
		if pobj['model'] != data['model']:
			raise wizard.except_wizard(_('UserError'), _('Incorrect report for this model !'))
    		pos_pobj.pprint(cr,uid,pobj, obj, context)
    return {}


class wizard_report(wizard.interface):

    states = {
        'init': {
            'actions': [ _update_wizard],
            'result': {'type':'form', 'arch': _select_form, 
		'fields': _select_fields, 
	    'state':[('end','Cancel'),('print','Print')]},
        },
        'print': {
            'actions': [_pos_print],
            'result': {'type':'state' , 'state':'end'},
        },
    }

wizard_report('wizard.point_of_sale_print.print')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
