# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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

import netsvc
from osv import fields, osv

class account_invoice(osv.osv):
    _inherit='account.invoice'
    _columns={
        'payment_type': fields.many2one('payment.type', 'Payment type'),
    }

    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False):
        # Copy partner data to invoice, also the new field payment_type
        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id)
        payment_type = False
        if partner_id:
            partner_line = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner_line:
                if type=='in_invoice' or type=='in_refund':
                    payment_type = partner_line.payment_type_supplier.id
                else:
                    payment_type = partner_line.payment_type_customer.id
            if payment_type:
                result['value']['payment_type'] = payment_type
        return self.onchange_payment_type(cr, uid, ids, payment_type, partner_id, result)

    def onchange_payment_type(self, cr, uid, ids, payment_type, partner_id, result = {'value': {}}):
        if payment_type and partner_id:
            bank_types = self.pool.get('payment.type').browse(cr, uid, payment_type).suitable_bank_types
            if bank_types: # If the payment type is related with a bank account
                bank_types = [bt.code for bt in bank_types]
                partner_bank_obj = self.pool.get('res.partner.bank')
                args = [('partner_id', '=', partner_id), ('default_bank', '=', 1), ('state', 'in', bank_types)]
                bank_account_id = partner_bank_obj.search(cr, uid, args)
                if bank_account_id:
                    result['value']['partner_bank'] = bank_account_id[0]
                    return result
        result['value']['partner_bank'] = False
        return result

    def action_move_create(self, cr, uid, ids, *args):
        ret = super(account_invoice, self).action_move_create(cr, uid, ids, *args)
        if ret:
            for inv in self.browse(cr, uid, ids):
                move_line_ids = []
                for move_line in inv.move_id.line_id:
                    if (move_line.account_id.type == 'receivable' or move_line.account_id.type == 'payable') and move_line.state != 'reconciled' and not move_line.reconcile_id.id:
                        move_line_ids.append(move_line.id)
                if len(move_line_ids) and inv.partner_bank:
                    aml_obj = self.pool.get("account.move.line")
                    aml_obj.write(cr, uid, move_line_ids, {'partner_bank': inv.partner_bank.id})
        return ret

account_invoice()
