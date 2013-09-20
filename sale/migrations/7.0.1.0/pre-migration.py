# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Sylvain LE GAL
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.openupgrade import openupgrade

column_renames = {
    'sale_order':[
        ('partner_invoice_id', None),
        ('partner_shipping_id', None),
        ('partner_order_id', None),
    ],
    'sale_order_line':[
        ('address_allotment_id', None),
        ('notes', None),
    ],
}

xmlid_renames = [
    ('sale.shop', 'sale.sale_shop_1'),
    ('sale.act_cancel3', 'sale_stock.act_cancel3'),
    ('sale.act_ship', 'sale_stock.act_ship'),
    ('sale.act_ship_cancel', 'sale_stock.act_ship_cancel'),
    ('sale.act_ship_end', 'sale_stock.act_ship_end'),
    ('sale.act_ship_except', 'sale_stock.act_ship_except'),
    ('sale.act_wait_ship', 'sale_stock.act_wait_ship'),
    ('sale.trans_router_wait_ship', 'sale_stock.trans_router_wait_ship'),
    ('sale.trans_ship_end_done', 'sale_stock.trans_ship_end_done'),
    ('sale.trans_ship_except_ship', 'sale_stock.trans_ship_except_ship'),
    ('sale.trans_ship_except_ship_cancel', 'sale_stock.trans_ship_except_ship_cancel'),
    ('sale.trans_ship_except_ship_end', 'sale_stock.trans_ship_except_ship_end'),
    ('sale.trans_ship_ship_end', 'sale_stock.trans_ship_ship_end'),
    ('sale.trans_ship_ship_except', 'sale_stock.trans_ship_ship_except'),
    ('sale.trans_wait_ship_cancel3', 'sale_stock.trans_wait_ship_cancel3'),
    ('sale.trans_wait_ship_ship', 'sale_stock.trans_wait_ship_ship'),
    ('sale.trans_router_wait_invoice_shipping', 'sale_stock.trans_router_wait_invoice_shipping'),
    ('sale.trans_wait_invoice_invoice', 'sale_stock.trans_wait_invoice_invoice'),
    ('sale.process_node_deliveryorder0', 'sale_stock.process_node_deliveryorder0'),
    ('sale.process_node_invoiceafterdelivery0', 'sale_stock.process_node_invoiceafterdelivery0'),
    ('sale.process_node_packinglist0', 'sale_stock.process_node_packinglist0'),
    ('sale.process_node_saleorderprocurement0', 'sale_stock.process_node_saleorderprocurement0'),
    ('sale.process_node_saleprocurement0', 'sale_stock.process_node_saleprocurement0'),
    ('sale.process_transition_deliver0', 'sale_stock.process_transition_deliver0'),
    ('sale.process_transition_invoiceafterdelivery0', 'sale_stock.process_transition_invoiceafterdelivery0'),
    ('sale.process_transition_packing0', 'sale_stock.process_transition_packing0'),
    ('sale.process_transition_saleorderprocurement0', 'sale_stock.process_transition_saleorderprocurement0'),
    ('sale.process_transition_saleprocurement0', 'sale_stock.process_transition_saleprocurement0'),
    ('sale.process_transition_action_assign0', 'sale_stock.process_transition_action_assign0'),
    ('sale.process_transition_action_cancel1', 'sale_stock.process_transition_action_cancel1'),
    ('sale.process_transition_action_cancel2', 'sale_stock.process_transition_action_cancel2'),
    ('sale.process_transition_action_cancelassignation0', 'sale_stock.process_transition_action_cancelassignation0'),
    ('sale.process_transition_action_forceassignation0', 'sale_stock.process_transition_action_forceassignation0'),
    ('sale.process_transition_action_validate0', 'sale_stock.process_transition_action_validate0'),
]

def migrate_postpaid_order_policy(cr):
    cr.execute("""
        UPDATE sale_order 
        SET order_policy = 'manual' 
        WHERE order_policy = 'postpaid' """)

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    migrate_postpaid_order_policy(cr)
