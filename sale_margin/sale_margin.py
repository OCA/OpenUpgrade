# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: partner.py 1007 2005-07-25 13:18:09Z kayhman $
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

from osv import fields,osv
import pooler
from tools import config
import time

class sale_order_line(osv.osv):
    _name = "sale.order.line"
    _inherit = "sale.order.line"
    def _product_margin(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = 0
            if line.product_id:
                res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.product_id.standard_price*line.product_uos_qty),2)
        return res

    _columns = {
        'margin': fields.function(_product_margin, method=True, string='Margin'),
    }
sale_order_line()

class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"

    def _product_margin(self, cr, uid, ids, field_name, arg, context):
        # need to check with new requirement
        id_set = ",".join(map(str, ids))        
        cr.execute("""
            SELECT
                s.id,
                COALESCE(SUM(l.price_unit*l.product_uos_qty*(100-l.discount)/100.0 - t.standard_price * l.product_uos_qty) - i.amount_untaxed,0)::decimal(16,2) AS amount
            FROM
                sale_order s
            LEFT OUTER JOIN sale_order_line l ON (s.id=l.order_id)
            LEFT JOIN product_product p ON (p.id=l.product_id)
            LEFT JOIN product_template t ON (t.id=p.product_tmpl_id)
            LEFT JOIN stock_picking sp on (s.id = sp.sale_id)
            LEFT JOIN picking_invoice_rel r on (sp.id = r.picking_id)
            LEFT JOIN account_invoice i on (i.id = r.invoice_id)
            WHERE
                s.id IN ("""+id_set+""") GROUP BY s.id,i.amount_untaxed """)
        res = dict(cr.fetchall())
        return res

    _columns = {
        'margin': fields.function(_product_margin, method=True, string='Margin'),
    }
sale_order()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    _columns = {
        'invoice_ids': fields.many2many('account.invoice', 'picking_invoice_rel', 'picking_id', 'invoice_id', 'Invoices', domain=[('type','=','in_invoice')]),
    }
    
    def create_invoice(self, cr, uid, ids, *args):
        # need to carify with new requirement
        res = False
        invoice_ids = []
        margin_deduce = 0.0
        picking_obj = self.pool.get('stock.picking')
        picking_obj.write(cr, uid, ids, {'invoice_state' : '2binvoiced'})
        res = picking_obj.action_invoice_create(cr, uid, ids, type='out_invoice', context={})
        invoice_ids = res.values()
        picking_obj.write(cr, uid, ids,{'invoice_ids':[[6,0,invoice_ids]]})
        for invoice in self.pool.get('account.invoice').browse(cr, uid, invoice_ids):
            margin_deduce += invoice.amount_untaxed
        picking = picking_obj.browse(cr, uid, ids)[0]
        sale_id = picking.sale_id.id
        sale_obj = self.pool.get('sale.order').browse(cr, uid, [sale_id])[0]
        return True
stock_picking()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

