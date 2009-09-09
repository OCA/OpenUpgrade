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

class account_move_line(osv.osv):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    def amount_to_pay(self, cr, uid, ids, name, arg={}, context={}):
        """ Return the amount still to pay regarding all the payment orders
        (excepting cancelled orders). The amount to pay can be negative (Refund invoices)"""
        if not ids:
            return {}
        cr.execute("""SELECT ml.id,
                    CASE WHEN ml.amount_currency < 0
                        THEN - ml.amount_currency
                        WHEN ml.amount_currency > 0
                        THEN ml.amount_currency
                        ELSE ml.credit - ml.debit
                    END -
                    (SELECT coalesce(sum(amount_currency),0)
                        FROM payment_line pl
                            INNER JOIN payment_order po
                                ON (pl.order_id = po.id)
                        WHERE move_line_id = ml.id
                        AND po.state != 'cancel') as amount
                    FROM account_move_line ml
                    WHERE id in (%s)""" % (",".join(map(str, ids))))
        r=dict(cr.fetchall())
        return r

    def _to_pay_search(self, cr, uid, obj, name, args):
        if not len(args):
            return []
        line_obj = self.pool.get('account.move.line')
        query = line_obj._query_get(cr, uid, context={})
        where = ' and '.join(map(lambda x: '''(SELECT
        CASE WHEN l.amount_currency < 0
            THEN - l.amount_currency
            WHEN l.amount_currency > 0
            THEN l.amount_currency
            ELSE l.credit - l.debit
        END - coalesce(sum(pl.amount_currency), 0)
        FROM payment_line pl
        INNER JOIN payment_order po ON (pl.order_id = po.id)
        WHERE move_line_id = l.id AND po.state != 'cancel')''' \
        + x[1] + str(x[2])+' ',args))

        cr.execute(('''SELECT l.id
            FROM account_move_line l
            INNER JOIN account_invoice i ON (l.move_id = i.move_id)
            WHERE l.account_id in (SELECT id
                FROM account_account
                WHERE type in %s AND active)
            AND reconcile_id is null
            AND i.id is not null
            AND ''' + where + ' and ' + query), (('payable','receivable'),) )
        res = cr.fetchall()
        if not len(res):
            return [('id','=','0')]
        return [('id','in',map(lambda x:x[0], res))]

    def _payment_type_get(self, cr, uid, ids, field_name, arg, context={}):
        result = {}
        invoice_obj = self.pool.get('account.invoice')
        for rec in self.browse(cr, uid, ids, context):
            result[rec.id] = (0,0)
            invoice_id = invoice_obj.search(cr, uid, [('move_id', '=', rec.move_id.id)])
            if invoice_id:
                inv = invoice_obj.browse(cr, uid, invoice_id[0])
                if inv.payment_type:
                    result[rec.id] = (inv.payment_type.id, self.pool.get('payment.type').browse(cr, uid, inv.payment_type.id).name)
            else:
                result[rec.id] = (0,0)
        return result

    def _payment_type_search(self, cr, uid, obj, name, args, context={}):
        if not len(args):
            return []
        text = args[0][2]
        if not text:
            return []
        ptype_id = self.pool.get('payment.type').search(cr,uid,[('name','ilike',text)])
        if ptype_id:
            cr.execute('SELECT l.id ' \
                'FROM account_move_line l, account_invoice i ' \
                'WHERE l.move_id = i.move_id AND i.payment_type in (%s)' % (','.join(map(str, ptype_id))))
            res = cr.fetchall()
            if len(res):
                return [('id', 'in', [x[0] for x in res])]
        return [('id','=','0')]

    _columns = {
        'received_check': fields.boolean('Received check', help="To write down that a check in paper support has been received, for example."),
        'partner_bank': fields.many2one('res.partner.bank','Bank Account'),
        'amount_to_pay' : fields.function(amount_to_pay, method=True, type='float', string='Amount to pay', fnct_search=_to_pay_search),
        'payment_type': fields.function(_payment_type_get, fnct_search=_payment_type_search, method=True, type="many2one", relation="payment.type", string="Payment type"),
    }

    def write(self, cr, uid, ids, vals, context=None, check=True, update_check=True):
        for key in vals.keys():
            if key not in ['received_check', 'partner_bank', 'date_maturity']:
                return super(account_move_line, self).write(cr, uid, ids, vals, context, check, update_check=True)
        return super(account_move_line, self).write(cr, uid, ids, vals, context, check, update_check=False)

account_move_line()
