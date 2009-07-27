# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                    Jordi Esteve <jesteve@zikzakmedia.com>
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
import time


class pos_order(osv.osv):
    _inherit = 'pos.order'

    def _amount_tax(self, cr, uid, ids, field_name, arg, context):
        """This method is redefined to deal with prices with/without taxes included depending on company configuration"""
        res = {}
        tax_obj = self.pool.get('account.tax')
        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, uid, context)
        prices_tax_include = user.company_id.pos_prices_tax_include

        for order in self.browse(cr, uid, ids):
            val = 0.0
            for line in order.lines:
                if prices_tax_include:
                    val = reduce(lambda x, y: x+round(y['amount'], 2),
                        tax_obj.compute_inv(cr, uid, line.product_id.taxes_id,
                            line.price_unit * \
                            (1-(line.discount or 0.0)/100.0), line.qty),
                            val)
                else:
                    val = reduce(lambda x, y: x+round(y['amount'], 2),
                        tax_obj.compute(cr, uid, line.product_id.taxes_id,
                            line.price_unit * \
                            (1-(line.discount or 0.0)/100.0), line.qty),
                            val)

            res[order.id] = val
        return res


    def _amount_total(self, cr, uid, ids, field_name, arg, context):
        """This method is redefined to deal with prices with/without taxes included depending on company configuration"""
        id_set = ",".join(map(str, ids))
        cr.execute("""
        SELECT
            p.id,
            COALESCE(SUM(
                l.price_unit*l.qty*(1-(l.discount/100.0)))::decimal(16,2), 0
                ) AS amount
        FROM pos_order p
            LEFT OUTER JOIN pos_order_line l ON (p.id=l.order_id)
        WHERE p.id IN (""" + id_set  +""") GROUP BY p.id """)
        res = dict(cr.fetchall())

        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, uid, context)
        prices_tax_include = user.company_id.pos_prices_tax_include

        for rec in self.browse(cr, uid, ids, context):
            if rec.partner_id \
               and rec.partner_id.property_account_position \
               and rec.partner_id.property_account_position.tax_ids:
                if prices_tax_include:
                    res[rec.id] = res[rec.id] - rec.amount_tax
            else:
                if not prices_tax_include:
                    res[rec.id] = res[rec.id] + rec.amount_tax
        return res


    _columns = {
        'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),
        'amount_total': fields.function(_amount_total, method=True, string='Total'),
    }


    def action_invoice(self, cr, uid, ids, context={}):
        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, uid, context)
        prices_tax_include = user.company_id.pos_prices_tax_include
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        inv_ids = []

        for order in self.browse(cr, uid, ids, context):
            if order.invoice_id:
                inv_ids.append(order.invoice_id.id)
                continue

            if not order.partner_id:
                raise osv.except_osv(_('Error'), _('Please provide a partner for the sale.'))

            inv = {
                'name': 'Invoice from POS: '+order.name,
                'origin': order.name,
                'type': 'out_invoice',
                'reference': order.name,
                'partner_id': order.partner_id.id,
                'comment': order.note or '',
                'price_type': prices_tax_include and 'tax_included' or 'tax_excluded'
            }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', order.partner_id.id)['value'])
            inv_id = inv_ref.create(cr, uid, inv, context)

            self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'})
            inv_ids.append(inv_id)

            for line in order.lines:
                inv_line = {
                    'invoice_id': inv_id,
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                    line.product_id.id,
                    line.product_id.uom_id.id,
                    line.qty, partner_id = order.partner_id.id, fposition_id=order.partner_id.property_account_position.id)['value'])
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount

                inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line)\
                    and [(6, 0, inv_line['invoice_line_tax_id'])] or []
                inv_line_ref.create(cr, uid, inv_line, context)

        for i in inv_ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', i, 'invoice_open', cr)
        return inv_ids


    def create_account_move(self, cr, uid, ids, context=None):
        """This method is redefined to deal with prices with/without taxes included depending on company configuration.
           The computation of taxes is fixed to take account the discount of each POS line: line.price_unit * (1-(line.discount or 0.0)/100.0)
           If pos.order has partner_id set, stores it in the account.move.line created by the pos order.
           POS orders with amount_total==0 no creates account moves (it gives error)"""
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        account_period_obj = self.pool.get('account.period')
        account_tax_obj = self.pool.get('account.tax')
        period = account_period_obj.find(cr, uid, context=context)[0]
        users_obj = self.pool.get('res.users')
        user = users_obj.browse(cr, uid, uid, context)
        prices_tax_include = user.company_id.pos_prices_tax_include

        for order in self.browse(cr, uid, ids, context=context):

            if order.amount_total == 0:
                continue

            to_reconcile = []
            group_tax = {}

            if order.amount_total > 0:
                order_account = order.sale_journal.default_credit_account_id.id
            else:
                order_account = order.sale_journal.default_debit_account_id.id

            # Create an entry for the sale
            move_id = account_move_obj.create(cr, uid, {
                'journal_id': order.sale_journal.id,
                'period_id': period,
                }, context=context)

            # Create an move for each order line
            for line in order.lines:

                tax_amount = 0
                if prices_tax_include:
                    computed_taxes = account_tax_obj.compute_inv(cr, uid, line.product_id.taxes_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.qty)
                else:
                    computed_taxes = account_tax_obj.compute(cr, uid, line.product_id.taxes_id, line.price_unit * (1-(line.discount or 0.0)/100.0), line.qty)

                for tax in computed_taxes:
                    tax_amount += round(tax['amount'], 2)
                    group_key = (tax['tax_code_id'],
                                tax['base_code_id'],
                                tax['account_collected_id'])

                    if group_key in group_tax:
                        group_tax[group_key] += round(tax['amount'], 2)
                    else:
                        group_tax[group_key] = round(tax['amount'], 2)

                amount = line.price_subtotal
                if prices_tax_include:
                    amount -= tax_amount

                # Search for the income account
                if  line.product_id.property_account_income.id:
                    income_account = line.\
                                    product_id.property_account_income.id
                elif line.product_id.categ_id.\
                        property_account_income_categ.id:
                    income_account = line.product_id.categ_id.\
                                    property_account_income_categ.id
                else:
                    raise osv.except_osv(_('Error !'), _('There is no income '\
                        'account defined for this product: "%s" (id:%d)') \
                        % (line.product_id.name, line.product_id.id, ))


                # Empty the tax list as long as there is no tax code:
                tax_code_id = False
                tax_amount = 0
                while computed_taxes:
                    tax = computed_taxes.pop(0)
                    if amount > 0:
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']
                    # If there is one we stop
                    if tax_code_id:
                        break

                # Create a move for the line
                account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': move_id,
                    'account_id': income_account,
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                    'tax_code_id': tax_code_id,
                    'tax_amount': tax_amount,
                    'partner_id': order.partner_id and order.partner_id.id or False
                }, context=context)

                # For each remaining tax with a code, whe create a move line
                for tax in computed_taxes:
                    if amount > 0:
                        tax_code_id = tax['base_code_id']
                        tax_amount = line.price_subtotal * tax['base_sign']
                    else:
                        tax_code_id = tax['ref_base_code_id']
                        tax_amount = line.price_subtotal * tax['ref_base_sign']
                    if not tax_code_id:
                        continue

                    account_move_line_obj.create(cr, uid, {
                        'name': order.name,
                        'date': order.date_order,
                        'ref': order.name,
                        'move_id': move_id,
                        'account_id': income_account,
                        'credit': 0.0,
                        'debit': 0.0,
                        'journal_id': order.sale_journal.id,
                        'period_id': period,
                        'tax_code_id': tax_code_id,
                        'tax_amount': tax_amount,
                        'partner_id': order.partner_id and order.partner_id.id or False
                    }, context=context)


            # Create a move for each tax group
            (tax_code_pos, base_code_pos, account_pos)= (0, 1, 2)
            for key, amount in group_tax.items():
                account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': move_id,
                    'account_id': key[account_pos],
                    'credit': ((amount>0) and amount) or 0.0,
                    'debit': ((amount<0) and -amount) or 0.0,
                    'journal_id': order.sale_journal.id,
                    'period_id': period,
                    'tax_code_id': key[tax_code_pos],
                    'tax_amount': amount,
                    'partner_id': order.partner_id and order.partner_id.id or False
                }, context=context)

            # counterpart
            to_reconcile.append(account_move_line_obj.create(cr, uid, {
                'name': order.name,
                'date': order.date_order,
                'ref': order.name,
                'move_id': move_id,
                'account_id': order_account,
                'credit': ((order.amount_total<0) and -order.amount_total)\
                    or 0.0,
                'debit': ((order.amount_total>0) and order.amount_total)\
                    or 0.0,
                'journal_id': order.sale_journal.id,
                'period_id': period,
                'partner_id': order.partner_id and order.partner_id.id or False
            }, context=context))


            # search the account receivable for the payments:
            account_receivable = order.sale_journal.default_credit_account_id.id
            if not account_receivable:
                raise  osv.except_osv(_('Error !'),
                    _('There is no receivable account defined for this journal:'\
                    ' "%s" (id:%d)') % (order.sale_journal.name, order.sale_journal.id, ))

            for payment in order.payments:

                if payment.amount > 0:
                    payment_account = \
                        payment.journal_id.default_debit_account_id.id
                else:
                    payment_account = \
                        payment.journal_id.default_credit_account_id.id

                if payment.amount > 0:
                    order_account = \
                        order.sale_journal.default_credit_account_id.id
                else:
                    order_account = \
                        order.sale_journal.default_debit_account_id.id

                # Create one entry for the payment
                payment_move_id = account_move_obj.create(cr, uid, {
                    'journal_id': payment.journal_id.id,
                    'period_id': period,
                }, context=context)
                account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': payment_move_id,
                    'account_id': payment_account,
                    'credit': ((payment.amount<0) and -payment.amount) or 0.0,
                    'debit': ((payment.amount>0) and payment.amount) or 0.0,
                    'journal_id': payment.journal_id.id,
                    'period_id': period,
                    'partner_id': order.partner_id and order.partner_id.id or False
                }, context=context)
                to_reconcile.append(account_move_line_obj.create(cr, uid, {
                    'name': order.name,
                    'date': order.date_order,
                    'ref': order.name,
                    'move_id': payment_move_id,
                    'account_id': order_account,
                    'credit': ((payment.amount>0) and payment.amount) or 0.0,
                    'debit': ((payment.amount<0) and -payment.amount) or 0.0,
                    'journal_id': payment.journal_id.id,
                    'period_id': period,
                    'partner_id': order.partner_id and order.partner_id.id or False
                }, context=context))

            account_move_obj.button_validate(cr, uid, [move_id, payment_move_id], context=context)
            account_move_line_obj.reconcile(cr, uid, to_reconcile, type='manual', context=context)
        return True


    def unlink(self, cr, uid, ids, context={}):
        """Allows delete pos orders in draft and cancel states"""
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state<>'draft' and rec.state<>'cancel':
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete a point of sale which is already confirmed !'))
        return super(osv.osv, self).unlink(cr, uid, ids, context=context)


    def create_picking(self, cr, uid, ids, context={}):
        """If pos.order has partner_id set, stores it in the stock.picking created by the pos order"""
        if super(pos_order, self).create_picking(cr, uid, ids, context):
            picking_obj = self.pool.get('stock.picking')
            partner_obj = self.pool.get('res.partner')
            for order in self.browse(cr, uid, ids, context=context):
                if order.partner_id:
                    # Cercar adreça enviament partner
                    address = partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery'])
                    p_ids = picking_obj.search(cr, uid, [('origin','=',order.name)])
                    #print order.partner_id.id, address, p_ids
                    picking_obj.write(cr, uid, p_ids, {'address_id': address['delivery']})
        return True


    #def action_invoice(self, cr, uid, ids, context={}):
        #"""Updates the invoice created by the pos order with bank account and type of payment info"""
        #inv_ids = super(pos_order, self).action_invoice(cr, uid, ids, context)
        #inv_obj = self.pool.get('account.invoice')
        #for inv_id in inv_ids:
            #inv = inv_obj.browse(cr, uid, inv_id, context)
            #value = inv_obj.onchange_partner_id2(cr, uid, [], 'out_invoice', inv.partner_id.id)['value']
            ##print value
            #inv_id = inv_obj.write(cr, uid, inv_id, value, context)
        #return inv_ids


    #def create_account_move(self, cr, uid, ids, context=None):
        #"""If pos.order has partner_id set, stores it in the account.move.line created by the pos order.
           #POS orders with amount_total==0 no creates account moves (it gives error)"""
        #for order in self.browse(cr, uid, ids, context=context):
            #if order.amount_total != 0:
                #if super(pos_order, self).create_account_move(cr, uid, [order.id], context):
                    #account_move_line_obj = self.pool.get('account.move.line')
                    #for order in self.browse(cr, uid, ids, context=context):
                        #if order.partner_id:
                            #m_ids = account_move_line_obj.search(cr, uid, [('name','=',order.name),('ref','=',order.name)])
                            ##print m_ids
                            #account_move_line_obj.write(cr, uid, m_ids, {'partner_id': order.partner_id.id})
        #return True

pos_order()


class pos_order_line(osv.osv):
    _inherit = 'pos.order.line'
    _order = "create_date desc"

    _columns = {
        'partner_id':fields.related('order_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
        'state':fields.related('order_id', 'state', type='selection', selection=[('cancel', 'Cancel'), ('draft', 'Draft'),
            ('paid', 'Paid'), ('done', 'Done'), ('invoiced', 'Invoiced')], string='State'),
    }

    def unlink(self, cr, uid, ids, context={}):
        """Allows delete pos orders in draft and cancel states"""
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state<>'draft' and rec.state<>'cancel':
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete a point of sale line which is already confirmed !'))
        return super(pos_order_line, self).unlink(cr, uid, ids, context=context)

pos_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

