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

from osv import fields,osv
import pooler
from tools import config
import time



class report_account_invoice_product(osv.osv):
    _name = 'report.account.invoice.product'
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
        ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Canceled')
        ],'State', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'amount': fields.float('Amount', readonly=True),
        'cost_price': fields.float('Cost Price', readonly=True),
        'margin': fields.float('Margin', readonly=True),
        'quantity': fields.float('Quantity', readonly=True),
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_account_invoice_product as (
                select
                    min(l.id) as id,
                    to_char(i.date_invoice, 'YYYY-MM-01') as name,
                    i.type,
                    i.state,
                    l.product_id,
                    sum(l.quantity * l.price_unit * (1.0 - l.discount/100.0)) as amount,
                    sum(l.quantity * l.cost_price) as cost_price,
                    sum((l.quantity * l.price_unit * (1.0 - l.discount/100.0) - (l.quantity * l.cost_price))) as margin,
                    sum(l.quantity) as quantity
                from account_invoice i
                    left join account_invoice_line l on (i.id = l.invoice_id)
                group by l.product_id, to_char(i.date_invoice, 'YYYY-MM-01'), i.type, i.state
            )
        """)
report_account_invoice_product()

class report_account_invoice_category(osv.osv):
    _name = 'report.account.invoice.category'
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
        ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Canceled')
        ],'State', readonly=True),
        'categ_id': fields.many2one('product.category', 'Categories', readonly=True),
        'amount': fields.float('Amount', readonly=True),
        'cost_price': fields.float('Cost Price', readonly=True),
        'margin': fields.float('Margin', readonly=True),
        'quantity': fields.float('Quantity', readonly=True),
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_account_invoice_category as (
                select
                    min(l.id) as id,
                    to_char(i.date_invoice, 'YYYY-MM-01') as name,
                    i.type,
                    i.state,
                    t.categ_id,
                    sum(l.quantity * l.price_unit * (1.0 - l.discount/100.0)) as amount,
                    sum(l.quantity * l.cost_price) as cost_price,
                    sum((l.quantity * l.price_unit * (1.0 - l.discount/100.0) - (l.quantity * l.cost_price))) as margin,
                    sum(l.quantity) as quantity
                from account_invoice i
                    left join account_invoice_line l on (i.id = l.invoice_id)
                    left join product_product p on (p.id = l.product_id)
                    left join product_template t on (t.id = p.product_tmpl_id)
                group by t.categ_id, to_char(i.date_invoice, 'YYYY-MM-01'), i.type, i.state
            )
        """)
report_account_invoice_category()

class report_account_invoice_partner(osv.osv):
    _name = 'report.account.invoice.partner'
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
        ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Canceled')
        ],'State', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'amount': fields.float('Amount', readonly=True),
        'cost_price': fields.float('Cost Price', readonly=True),
        'margin': fields.float('Margin', readonly=True),
        'quantity': fields.float('Quantity', readonly=True),
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_account_invoice_partner as (
                select
                    min(l.id) as id,
                    to_char(i.date_invoice, 'YYYY-MM-01') as name,
                    i.type,
                    i.state,
                    i.partner_id,
                    sum(l.quantity * l.price_unit * (1.0 - l.discount/100.0)) as amount,
                    sum(l.quantity * l.cost_price) as cost_price,
                    sum((l.quantity * l.price_unit * (1.0 - l.discount/100.0) - (l.quantity * l.cost_price))) as margin,
                    sum(l.quantity) as quantity
                from account_invoice i
                    left join account_invoice_line l on (i.id = l.invoice_id)
                group by i.partner_id, to_char(i.date_invoice, 'YYYY-MM-01'), i.type, i.state
            )
        """)
report_account_invoice_partner()

class report_account_invoice_partner_product(osv.osv):
    _name = 'report.account.invoice.partner.product'
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
        ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Canceled')
        ],'State', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'amount': fields.float('Amount', readonly=True),
        'cost_price': fields.float('Cost Price', readonly=True),
        'margin': fields.float('Margin', readonly=True),
        'quantity': fields.float('Quantity', readonly=True),
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_account_invoice_partner_product as (
                select
                    min(l.id) as id,
                    to_char(i.date_invoice, 'YYYY-MM-01') as name,
                    i.type,
                    i.state,
                    i.partner_id,
                    l.product_id,
                    sum(l.quantity * l.price_unit * (1.0 - l.discount/100.0)) as amount,
                    sum(l.quantity * l.cost_price) as cost_price,
                    sum((l.quantity * l.price_unit * (1.0 - l.discount/100.0) - (l.quantity * l.cost_price))) as margin,
                    sum(l.quantity) as quantity
                from account_invoice i
                    left join account_invoice_line l on (i.id = l.invoice_id)
                group by i.partner_id, l.product_id, to_char(i.date_invoice, 'YYYY-MM-01'), i.type, i.state
            )
        """)
report_account_invoice_partner_product()


class report_account_invoice(osv.osv):
    _name = 'report.account.invoice'
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
        ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('open','Open'),
            ('paid','Paid'),
            ('cancel','Canceled')
        ],'State', readonly=True),
        'amount': fields.float('Amount', readonly=True),
        'cost_price': fields.float('Cost Price', readonly=True),
        'margin': fields.float('Margin', readonly=True),
        'quantity': fields.float('Quantity', readonly=True),
    }
    _order = 'name desc'
    def init(self, cr):
        cr.execute("""
            create or replace view report_account_invoice as (
                select
                    min(l.id) as id,
                    to_char(i.date_invoice, 'YYYY-MM-01') as name,
                    i.type,
                    i.state,
                    sum(l.quantity * l.price_unit * (1.0 - l.discount/100.0)) as amount,
                    sum(l.quantity * l.cost_price) as cost_price,
                    sum((l.quantity * l.price_unit * (1.0 - l.discount/100.0) - (l.quantity * l.cost_price))) as margin,
                    sum(l.quantity) as quantity
                from account_invoice i
                    left join account_invoice_line l on (i.id = l.invoice_id)
                group by to_char(i.date_invoice, 'YYYY-MM-01'), i.type, i.state
            )
        """)
report_account_invoice()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

