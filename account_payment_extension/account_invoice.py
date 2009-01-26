# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2009 Zikzakmedia S.L. (http://www.zikzakmedia.com) All Rights Reserved.
# Copyright (c) 2008 Pablo Rocandio (salbet@gmail.com) All Rights Reserved.
# Copyright (c) 2006 ACYSOS S.L. (http://acysos.com) All Rights Reserved.
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
