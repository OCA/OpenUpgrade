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
from osv import osv, fields
from mx import DateTime

class AccountInvoice(osv.osv):
    _inherit = 'account.invoice'

    def _amount_to_pay(self, cursor, user, ids, name, args, context=None):
        '''Return the amount still to pay regarding all the payment orders'''
        if not ids:
            return {}
        res = {}
        for invoice in self.browse(cursor, user, ids, context=context):
            res[invoice.id] = 0.0
            if invoice.move_id:
                for line in invoice.move_id.line_id:
                    if not line.date_maturity or \
                            DateTime.strptime(line.date_maturity, '%Y-%m-%d') \
                            < DateTime.now():
                        res[invoice.id] += line.amount_to_pay
        return res

    _columns = {
        'partner_bank': fields.many2one('res.partner.bank', 'Bank Account',
            help='The partner bank account to pay\nKeep empty to use the default'),
        'amount_to_pay': fields.function(_amount_to_pay, method=True,
            type='float', string='Amount to be paid',
            help='The amount which should be paid at the current date\n' \
                    'minus the amount which is already in payment order'),
    }

    def onchange_partner_bank(self, cursor, user, ids, partner_bank_id):
        return {'value': {}}

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
            date_invoice=False, payment_term=False, partner_bank_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(cr, uid, ids, type,
                partner_id, date_invoice, payment_term)
        bank_id = False
        if partner_id:
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if p.bank_ids:
                bank_id = p.bank_ids[0].id

        if type in ('in_invoice', 'in_refund'):
            res['value']['partner_bank'] = bank_id

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            res['value'].update(to_update['value'])
        return res

AccountInvoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

