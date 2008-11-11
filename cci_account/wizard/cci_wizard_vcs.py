# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

_form="""<?xml version="1.0"?>
<form string="Are you sure?" colspan="4">
    <label string="Make Sure that the invoice has invoice number." />
</form>
"""

_fields = {
           }

class wizard_report(wizard.interface):

    def _get_defaults(self, cr, uid, data, context):
        inv_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        for obj_inv in inv_obj.browse(cr,uid,data['ids']):
            if obj_inv.type not in ('out_invoice','out_refund'):
                raise wizard.except_wizard('User Error!','VCS is associated with Customer Invoices and Refund only.')
            if not obj_inv.number:
                raise wizard.except_wizard('Data Insufficient!','No Invoice Number Associated with the Invoice ID '+ str(obj_inv.id) +'!')
        return data['form']

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':_form, 'fields':_fields, 'state':[('report','Ok')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'cci.vcs', 'state':'end'}
        }
    }
wizard_report('wizard.cci.vcs')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

