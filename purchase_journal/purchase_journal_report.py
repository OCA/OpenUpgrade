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

class report_purchase_journal_purchase(osv.osv):
    _name = "purchase_journal.purchase.stats"
    _description = "Purchases Orders by Journal"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'state': fields.selection([
            ('draft', 'Request for Quotation'),
            ('wait', 'Waiting'),
            ('confirmed', 'Confirmed'),
            ('approved', 'Approved'),
            ('except_ship', 'Shipping Exception'),
            ('except_invoice', 'Invoice Exception'),
            ('done', 'Done'), ('cancel', 'Cancelled')], 'Order State', readonly=True,
            select=True),
        'journal_id':fields.many2one('purchase_journal.purchase.journal', 'Journal', readonly=True),
        'quantity': fields.float('Quantities', readonly=True),
        'price_total': fields.float('Total Price', readonly=True),
        'price_average': fields.float('Average Price', readonly=True),
        'count': fields.integer('# of Lines', readonly=True),
    }
    _order = 'journal_id,name desc,price_total desc'
    def init(self, cr):
        cr.execute("""
            create or replace view purchase_journal_purchase_stats as (
                select
                    min(l.id) as id,
                    to_char(s.date_order, 'YYYY-MM-01') as name,
                    s.state,
                    s.journal_id,
                    sum(l.product_qty) as quantity,
                    count(*),
                    sum(l.product_qty*l.price_unit) as price_total,
                    (sum(l.product_qty*l.price_unit)/sum(l.product_qty))::decimal(16,2) as price_average
                from purchase_order s
                    right join purchase_order_line l on (s.id=l.order_id)
                group by s.journal_id, to_char(s.date_order, 'YYYY-MM-01'),s.state
            )
        """)
report_purchase_journal_purchase()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

