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
from osv import fields, osv

class AccountMoveLine(osv.osv):
    _inherit = 'account.move.line'

    def _invoice(self, cursor, user, ids, name, arg, context=None):
        invoice_obj = self.pool.get('account.invoice')
        res = {}
        for line_id in ids:
            res[line_id] = False
        cursor.execute('SELECT l.id, i.id ' \
                'FROM account_move_line l, account_invoice i ' \
                'WHERE l.move_id = i.move_id ' \
                    'AND l.id in (' + ','.join([str(x) for x in ids]) + ')')
        invoice_ids = []
        for line_id, invoice_id in cursor.fetchall():
            res[line_id] = invoice_id
            invoice_ids.append(invoice_id)
        invoice_names = {False: ''}
        for invoice_id, name in invoice_obj.name_get(cursor, user,
                invoice_ids, context=context):
            invoice_names[invoice_id] = name
        for line_id in res.keys():
            invoice_id = res[line_id]
            res[line_id] = (invoice_id, invoice_names[invoice_id])
        return res

    def _invoice_search(self, cursor, user, obj, name, args):
        if not len(args):
            return []
        invoice_obj = self.pool.get('account.invoice')

        i = 0
        while i < len(args):
            fargs = args[i][0].split('.', 1)
            if len(fargs) > 1:
                args[i] = (frags[0], 'in', invoice_obj.search(cursor, user,
                    [(fargs[1], args[i][1], args[i][2])]))
                i += 1
                continue
            if isinstance(args[i][2], basestring):
                res_ids = invoice_obj.name_search(cursor, user, args[i][2], [],
                        args[i][1])
                args[i] = (args[i][0], 'in', [x[0] for x in res_ids])
            i += 1
        qu1, qu2 = [], []
        for x in args:
            if x[1] != 'in':
                if (x[2] is False) and (x[1] == '='):
                    qu1.append('(i.id IS NULL)')
                elif (x[2] is False) and (x[1] == '<>' or x[1] == '!='):
                    qu1.append('(i.id IS NOT NULL)')
                else:
                    qu1.append('(i.id %s %s)' % (x[1], '%d'))
                    qu2.append(x[2])
            elif x[1] == 'in':
                if len(x[2]) > 0:
                    qu1.append('(i.id in (%s))' % (','.join(['%d'] * len(x[2]))))
                    qu2 += x[2]
                else:
                    qu1.append(' (False)')
        if len(qu1):
            qu1 = ' AND' + ' AND'.join(qu1)
        else:
            qu1 = ''
        cursor.execute('SELECT l.id ' \
                'FROM account_move_line l, account_invoice i ' \
                'WHERE l.move_id = i.move_id ' + qu1, qu2)
        res = cursor.fetchall()
        if not len(res):
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]

    _columns = {
        'invoice': fields.function(_invoice, method=True, string='Invoice',
            type='many2one', relation='account.invoice', fnct_search=_invoice_search),
    }

    def line2bank(self, cr, uid, ids, payment_type='manual', context=None):
        payment_mode_obj = self.pool.get('payment.mode')
        line2bank = {}
        if not ids:
            return {}
        bank_type = payment_mode_obj.suitable_bank_types(cr, uid, payment_type,
                context=context)
        for line in self.browse(cr, uid, ids, context=context):
            if line.invoice and line.invoice.partner_bank:
                line2bank[line.id] = line.invoice.partner_bank.id
            elif line.partner:
                for bank in line.partner.bank_ids:
                    if bank.state in bank_type:
                        line2bank[line.id] = bank.id
                        break
                if line.id not in line2bank and line.partner.bank_ids:
                    line2bank[line.id] = line.partner.bank_ids[0].id
        return line2bank

AccountMoveLine()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

