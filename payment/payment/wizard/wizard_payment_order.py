##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
import math
from osv import osv
from tools.misc import UpdateableStr
import pooler
import netsvc
from osv import fields


payment_form = """<?xml version="1.0"?>
<form string="Payment Order">
  <field name="type"/>
  <field name="payment_date"/>
</form>"""
def type_get(self,cr,uid,context):

    pay_type_obj = pooler.get_pool(cr.dbname).get('payment.type')
    ids = pay_type_obj.search(cr, uid, [])
    res = pay_type_obj.read(cr, uid, ids, ['code','name'], context)
    print str(res)

    return [(r['code'],r['name']) for r in res]

def _make_payment(self, cr, uid, data, contexts):
    form = data['form']
    pay_type_obj = pooler.get_pool(cr.dbname).get('account.invoice')
    ids = pay_type_obj.search(cr, uid, [(' amount_to_pay ', '>', '0'),('date_due ', '<', form['payment_date'])])
    #ids = pay_type_obj.search(cr, uid, [])
    res=pay_type_obj.read(cr, uid, ids, ['id','amount_total'])
    print str(res)
    pay_obj = pooler.get_pool(cr.dbname).get('payment.order')
    pay_order = {
           'name':form['payment_date'],
           'state':'draft',
           'type':form['type'],

          }
    pay_id=pay_obj.create(cr,uid,pay_order)
    pay_order_line = pooler.get_pool(cr.dbname).get('payment.line')


    if res:
        for i in range(len(res)):
            pay_line = {
                   'invoice_id':res[i]['id'],
                   'amount':res[i]['amount_total'],
                   'order_id':pay_id,
                    }
            pay_order_line.create(cr,uid,pay_line)





    return {}

payment_fields = {
    'type' : {'string':'Payment Type','type':'selection','selection':type_get,'default':lambda *a:'manual'},
    'payment_date' : {'string':"Date", 'type':'date'}

}


#FIXME: this doesn't do anything...

class wizard_payment_order(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type':'form', 'arch':payment_form, 'fields':payment_fields, 'state':[('end', 'Cancel'),('payment','Make Payement')]}

                },

        'payment': {
             'actions' : [_make_payment],
             'result' : {'type' : 'state', 'state':'end'}

                    }
    }
wizard_payment_order('payment.order.make_payment')
