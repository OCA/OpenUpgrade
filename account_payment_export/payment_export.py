# -*- encoding: utf-8 -*-
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

import time
from osv import osv,fields
import netsvc
import pooler


class account_pay(osv.osv):
    _name = "account.pay"
    _description = "Payment Export History"
    _columns = {
        'name': fields.binary('Export File', readonly=True,required=True),
        'info': fields.char('Information',size=50,readonly=True),
        'note': fields.text('Creation Log', readonly=True),
    }
account_pay()


class res_partner_bank(osv.osv):
    _inherit = "res.partner.bank"
    _columns = {
                'institution_code':fields.char('Institution Code', size=3),
                'acc_number': fields.char('Account number', size=64, required=True),
                'iban': fields.char('IBAN', size=34, required=True,help="International Bank Account Number"),
    }

    def fields_get(self, cr, uid, fields=None, context=None):
        return super(osv.osv, self).fields_get(cr, uid, fields, context)

    def name_get(self, cr, uid, ids, context=None):
            result=[]
            if not len(ids):
                return []
            ret_name=''
            ret_id=False

            for bank in self.browse(cr, uid, ids, context=context):

                ret_id=bank.id
                if bank.state=='bank':
                    ret_name=str(bank.acc_number)
                    if bank.bank:
                        ret_name +="("+bank.bank.name + ")"
                elif bank.state=='iban':
                    ret_name=str(bank.iban)
                    if bank.bank:
                        ret_name +="("+bank.bank.name + ")"
                else:
                    ret_id,ret_name=super(res_partner_bank,self).name_get(cr, uid, [bank.id], context=context)[0]
                result.append((ret_id,ret_name))

            return result
res_partner_bank()


class payment_order(osv.osv):
    _inherit = "payment.order"

    def get_wizard(self,mode):
        if mode=='pay':
            return self._module,'wizard_account_payment_create'
        return super(payment_order,self).get_wizard(mode)
payment_order()


class res_bank(osv.osv):
    _inherit = "res.bank"

    _columns={
     'bilateral':fields.char('Bilateral Relationship', size=12),
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

