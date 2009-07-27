# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Zikzakmedia SL (http://www.zikzakmedia.com) All Rights Reserved.
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

import pooler
import netsvc
import wizard
import time
from tools.misc import UpdateableStr

def _get_journal(self, cr, uid, context):
    pool = pooler.get_pool(cr.dbname)

    users_obj = pool.get('res.users')
    user = users_obj.browse(cr, uid, uid, context)
    journals = user.company_id.pos_journals

    if journals:
        res = [(j.id, j.name) for j in journals]
    else:
        obj = pool.get('account.journal')
        ids = obj.search(cr, uid, [('type', '=', 'cash')])
        res = obj.read(cr, uid, ids, ['id', 'name'], context)
        res = [(r['id'], r['name']) for r in res]
    return res


payment_form = """<?xml version="1.0"?>
<form string="Add payment:">
    <field name="amount" />
    <field name="journal"/>
    <field name="payment_id" />
    <field name="payment_date" />
    <field name="payment_nb" />
    <field name="payment_name" />
    <field name="invoice_wanted" />
</form>
"""

payment_fields = {
    'amount': {'string': 'Amount', 'type': 'float', 'required': True},
    'invoice_wanted': {'string': 'Invoice', 'type': 'boolean', 'help': "To create invoice, for example if you are billing membership fees. Then the payment in the point of sale has no sense, because the payments will be managed from the menu Financial management / Payment."},
    'journal': {'string': 'Journal',
            'type': 'selection',
            'selection': _get_journal,
            'required': True,
        },
    'payment_id': {'string': 'Payment term', 'type': 'many2one', 'relation': 'account.payment.term', 'required': True},
    'payment_date': {'string': 'Payment date', 'type': 'date', 'required': True},
    'payment_name': {'string': 'Payment name', 'type': 'char', 'size': '32'},
    'payment_nb': {'string': 'Piece number', 'type': 'char', 'size': '32'},
    }

sale_order_warning_form = """<?xml version="1.0" encoding="utf-8"?>
<form string="Add payment:">
    <label string="This partner has already made an order with the product:" colspan="4"/>
    <field name="product" colspan="4" nolabel="1"/>
    <label string=""/>
    <label string="Maybe you may want to create the sale from the existing order:" colspan="4"/>
    <field name="sale_order" colspan="4" nolabel="1"/>
</form>"""

sale_order_warning_fields = {
    'product': {'string': 'Product', 'type': 'char', 'size': '128', 'readonly': True},
    'sale_order': {'string': 'Order', 'type': 'char', 'size': '128', 'readonly': True},
}

product_stock_warning_form = """<?xml version="1.0" encoding="utf-8"?>
<form string="Add payment:">
    <label string="These products have not enough virtual stock:" colspan="4"/>
    <label string=""/>
    <field name="product" colspan="4" nolabel="1" />
</form>"""

product_stock_warning_fields = {
    'product': {'string': 'Product', 'type': 'char', 'size': '128', 'readonly': True},
}

sale_order_info = UpdateableStr()
product_info = UpdateableStr()

class pos_payment(wizard.interface):
    def _pre_init(self, cr, uid, data, context):

        def _get_journal(pool, order):
            j_obj = pool.get('account.journal')

            journal_to_fetch = 'DEFAULT'
            if order.amount_total < 0:
                journal_to_fetch = 'GIFT'
            else:
                if order.amount_paid > 0:
                    journal_to_fetch = 'REBATE'

            pos_config_journal = pool.get('pos.config.journal')
            ids = pos_config_journal.search(cr, uid, [('code', '=', journal_to_fetch)])
            objs = pos_config_journal.browse(cr, uid, ids)
            if objs:
                journal = objs[0].journal_id.id
            else:
                existing = [payment.journal_id.id for payment in order.payments]
                ids = j_obj.search(cr, uid, [('type', '=', 'cash')])
                for i in ids:
                    if i not in existing:
                        journal = i
                        break
                if not journal:
                    journal = ids[0]

            return journal

        pool = pooler.get_pool(cr.dbname)
        order = pool.get('pos.order').browse(cr, uid, data['id'], context)

        # get amount to pay:
        amount = order.amount_total - order.amount_paid

        # get journal:
        journal = _get_journal(pool, order)

        # check if an invoice is wanted:
        #invoice_wanted_checked = not not order.partner_id # not not -> boolean
        # Membership products need invoice
        invoice_wanted_checked = False
        for line in order.lines:
            if line.product_id.membership:
                invoice_wanted_checked = True
                break

        # select the current date
        current_date = time.strftime('%Y-%m-%d')

        return {'journal': journal, 'amount': amount, 'invoice_wanted': invoice_wanted_checked, 'payment_date': current_date}


    def _add_pay(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        order_obj = pool.get('pos.order')
        result = data['form']

        invoice_wanted = data['form']['invoice_wanted']

        # add 'invoice_wanted' in 'pos.order'
        order_obj.write(cr, uid, [data['id']], {'invoice_wanted': invoice_wanted})

        order_obj.add_payment(cr, uid, data['id'], result, context=context)
        return {}


    def _pre_check(self, cr, uid, data, context):
        """Check if the order has lines"""
        pool = pooler.get_pool(cr.dbname)
        order_obj = pool.get('pos.order')
        order = order_obj.browse(cr, uid, data['id'], context)
        if not order.lines:
            raise wizard.except_wizard(_('Error'), _("No products have been added."))
        return {}


    def _check(self, cr, uid, data, context):
        """Check the order:
        if the order is not paid: continue payment,
        if the order is paid print invoice (if wanted) or ticket.
        """
        pool = pooler.get_pool(cr.dbname)
        order_obj = pool.get('pos.order')
        order = order_obj.browse(cr, uid, data['id'], context)
        #if not order.amount_total:
        #   return 'receipt'
        order_obj.test_order_lines(cr, uid, order, context=context)

        action = 'ask_pay'
        if order.state == 'paid':
            if order.partner_id:
                if order.invoice_wanted:
                    action = 'invoice'
                else:
                    action = 'receipt'
            else:
                action = 'receipt'
        else:
            users_obj = pool.get('res.users')
            user = users_obj.browse(cr, uid, uid, context)
            # Check if the partner has other pickings with the same products
            if user.company_id.pos_warn_sale_order and order.partner_id:
                address_ids = [adr.id for adr in order.partner_id.address]
                #print address_ids, order.last_out_picking.id
                picking_obj = pool.get('stock.picking')
                picking_ids = picking_obj.search(cr, uid, [('state','in',['auto','confirmed','assigned']), ('id','!=',order.last_out_picking.id), ('address_id','in',address_ids)])
                if picking_ids:
                    product_ids = [line.product_id.id for line in order.lines]
                    #print product_ids
                    for picking in picking_obj.browse(cr, uid, picking_ids, context):
                        for m in picking.move_lines:
                            if m.product_id.id in product_ids:
                                product_info.string = (m.product_id.name).encode('utf-8')
                                sale_order_info.string = (picking.origin and picking.name+'-'+picking.origin or picking.name).encode('utf-8')
                                action = 'sale_order_warning'
                                return action
            # Check the product stock of the order lines
            if user.company_id.pos_warn_virtual_stock:
                product = []
                for line in order.lines:
                    if line.product_id.type != 'service' and line.product_id.virtual_available - line.qty < 0:
                        product.append(line.product_id.name)
                if product:
                    product_info.string = (', '.join(product)).encode('utf-8')
                    action = 'product_stock_warning'
                    return action

        return action


    def _pre_warning(self, cr, uid, data, context):
        return {'product': product_info.string, 'sale_order': sale_order_info.string}


    def create_invoice(self, cr, uid, data, context):
        wf_service = netsvc.LocalService("workflow")
        for i in data['ids']:
            wf_service.trg_validate(uid, 'pos.order', i, 'invoice', cr)
        return {}


    states = {
        'init': {
            'actions': [_pre_check],
            'result': {
                'type': 'choice',
                'next_state': _check,
            }
        },
        'sale_order_warning': {
            'actions': [_pre_warning],
            'result': {
                'type': 'form',
                'arch': sale_order_warning_form,
                'fields': sale_order_warning_fields,
                'state': (('end', 'Cancel'), ('ask_pay', 'Go on', 'gtk-ok', True))
            }
        },
        'product_stock_warning': {
            'actions': [_pre_warning],
            'result': {
                'type': 'form',
                'arch': product_stock_warning_form,
                'fields': product_stock_warning_fields,
                'state': (('end', 'Cancel'), ('ask_pay', 'Go on', 'gtk-ok', True))
            }
        },
        'ask_pay': {
            'actions': [_pre_init],
            'result': {
                'type': 'form',
                'arch': payment_form,
                'fields': payment_fields,
                'state': (('end', 'Cancel'), ('add_pay', 'Ma_ke payment', 'gtk-ok', True)
                         )
            }
        },
        'add_pay': {
            'actions': [_add_pay],
            'result': {
                'type': 'state',
                'state': "init",
            }
        },
        'invoice': {
            'actions': [create_invoice],
            'result': {
                'type': 'print',
                'report': 'pos.invoice',
                'state': 'end'
            }
        },
        'receipt': {
            'actions': [],
            'result': {
                'type': 'print',
                'report': 'pos.receipt',
                'state': 'end'
            }
        },
        'paid': {
            'actions': [],
            'result': {
                'type': 'state',
                'state': 'end'
            }
        },

    }

pos_payment('pos.payment2')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

