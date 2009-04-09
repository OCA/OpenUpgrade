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

pay_form = '''<?xml version="1.0"?>
<form title="Paid ?">
    <field name="first"/>
    <field name="last"/>
    <field name="quantity"/>
    <field name="price"/>
    <field name="value"/>
    <field name="account_id"/>
</form>'''

pay_fields = {
    'first': {'string':u'De', 'type':'integer', 'readonly':True},
    'last': {'string':u'a', 'type':'integer', 'readonly':True},
    'quantity': {'string':u'Quantité', 'type':'integer', 'readonly':True},
    'price': {'string':u'Prix unitaire', 'type':'float', 'readonly':True},
    'value': {'string':u'Montant a payer', 'type':'float', 'readonly':True},
    'account_id': {'string':u'Compte destination', 'type':'many2one', 'required':True, 'relation':'account.account', 'domain':[('type','=','cash')]},
}

def _get_value(self,cr, uid, datas,context):
    vign_obj = pooler.get_pool(cr.dbname).get('huissier.vignettes')
    res = vign_obj.browse(cr, uid, datas['ids'],context)[0]
#   service = netsvc.LocalService("object_proxy")
#   res = service.execute(uid, 'huissier.vignettes', 'read', datas['ids'], ['first', 'last', 'quantity', 'price', 'value'])
    if not res:
        return {}
    print "GET VALUE",res.value or False
    return {'first':res.first, 'last':res.last, 'quantity':res.quantity,'price':res.price, 'value':res.value }
    
def _pay_labels(self,cr, uid, datas,context):
    print "_pay_labels"
    vign_obj = pooler.get_pool(cr.dbname).get('huissier.vignettes')
    ids = vign_obj.pay(cr, uid, datas['id'], datas['form']['account_id'])
    cr.commit()

#   service = netsvc.LocalService("object_proxy")
#   pay_id = service.execute(uid, 'huissier.vignettes', 'pay', [datas['id']], datas['form']['account_id'])
    return {}

class wizard_pay_labels(wizard.interface):
    states = {
        'init': {
            'actions': [_get_value], 
            'result': {'type': 'form', 'arch':pay_form, 'fields':pay_fields, 'state':[('pay','Payer les vignettes'), ('end','Annuler')]}
        },
        'pay': {
            'actions': [_pay_labels],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wizard_pay_labels('huissier.labels.pay')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

