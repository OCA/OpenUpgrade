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

import time
import pooler
import wizard
import netsvc

close_form = '''<?xml version="1.0"?>
<form title="Paid ?">
    <field name="adj"/>
    <field name="frais"/>
    <field name="total"/>
    <field name="salle"/>
    <newline/>
    <field name="voirie"/>
</form>'''

close_fields = {
    'adj': {'string':'Adjudications', 'type':'float', 'readonly':True},
    'frais': {'string':'Frais', 'type':'float', 'readonly':True},
    'total': {'string':'Total', 'type':'float', 'readonly':True},
    'salle': {'string':'Frais de salle', 'type':'float', 'readonly':True},
    'voirie': {'string':'Frais de voirie', 'type':'float'},
}


class wizard_invoice_deposit(wizard.interface):
    def _invoice_deposit(self,cr, uid, datas,context):
    #   service = netsvc.LocalService("object_proxy")
    #   invoice_id = service.execute(uid, 'huissier.deposit', 'invoice_once', datas['ids'])
        order_obj = pooler.get_pool(cr.dbname).get('huissier.deposit')
        ids = order_obj.invoice_once(cr, uid, datas['ids'],context)
        cr.commit()
    #   return {
    #   'domain': "[('id','in', ["+','.join(map(str,ids))+"])]",
    #   'name': 'Garde invoices',
    #   'view_type': 'form',
    #   'view_mode': 'tree,form',
    #   'res_model': 'account.invoice',
    #   'view_id': False,
    #   'context': "{'type':'out_refund'}",
    #   'type': 'ir.actions.act_window'
    #   }
        return {'ids':[ids]}
    
    states = {
        'init': {
            'actions': [_invoice_deposit],
            'result': {'type':'print', 'report':'account.invoice', 'get_id_from_action':True, 'state':'end'}
        }
    }
wizard_invoice_deposit('huissier.deposit.invoice')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

