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
from osv import osv,fields
import netsvc
import pooler

class account_pay(osv.osv):
    _name = "account.pay"
    _description = "Payment Export History"
    _rec_name = 'payment_order_id'
    _columns = {
        'payment_order_id': fields.many2one('payment.order', 'Payment Order Reference',readonly=True),
        'state': fields.selection([('failed','Failed'),('succeeded', 'Succeeded')],'Status',readonly=True),
        'file': fields.binary('Saved File', readonly=True),
        'note': fields.text('Creation Log', readonly=True),
        'create_date': fields.datetime('Creation Date',required=True, readonly=True),
        'create_uid': fields.many2one('res.users', 'Creation User', required=True, readonly=True),
    }
account_pay()

class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"
    _columns = {
                'institution_code':fields.char('Institution Code', size=3), 
                #what is it used for?
                #if it's a code of the financial institution of the ordering customer, why is it on res_partner_bank and not on res_bank?


#                'acc_number': fields.char('Account number', size=64, required=True),
#                'iban': fields.char('IBAN', size=34, required=True,help="International Bank Account Number"),
    }

    #~ def fields_get(self, cr, uid, fields=None, context=None):
        #~ return super(osv.osv, self).fields_get(cr, uid, fields, context)

    #~ def name_get(self, cr, uid, ids, context=None):
            #~ result=[]
            #~ if not len(ids):
                #~ return []
            #~ ret_name=''
            #~ ret_id=False

            #~ for bank in self.browse(cr, uid, ids, context=context):

                #~ ret_id=bank.id
                #~ if bank.state=='bank':
                    #~ ret_name=str(bank.acc_number)
                    #~ if bank.bank:
                        #~ ret_name +="("+bank.bank.name + ")"
                #~ elif bank.state=='iban':
                    #~ ret_name=str(bank.iban)
                    #~ if bank.bank:
                        #~ ret_name +="("+bank.bank.name + ")"
                #~ else:
                    #~ ret_id,ret_name=super(res_partner_bank,self).name_get(cr, uid, [bank.id], context=context)[0]
                #~ result.append((ret_id,ret_name))

            #~ return result
res_partner_bank()



# ?????
#~ class payment_order(osv.osv):
    #~ _inherit = "payment.order"

    #~ def get_wizard(self,mode):
        #~ if mode=='pay':
            #~ return self._module,'wizard_account_payment_create'
        #~ return super(payment_order,self).get_wizard(mode)
#~ payment_order()


class res_bank(osv.osv):
    _inherit = "res.bank"

    _columns={
     'bilateral':fields.char('Bilateral Relationship', size=12, help="This field may contain indications on the processing to be applied, e.g. an indication concerning the globalisation of these payments.The content of this field must be laid down on a bilateral basis between the bank and its client."),
    }

res_bank()

class payment_method(osv.osv):
    _name="payment.method"
    _description="Payment Method For Export"

    _columns = {
        'name': fields.char('Code',size=3,required=True),
        'description': fields.text('Description'),
    }

payment_method()

class charges_code(osv.osv):
    _name="charges.code"
    _description="Charges Codes For Export"

    _columns = {
        'name': fields.char('Code',size=3,required=True),
        'description': fields.text('Description'),
    }

charges_code()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

