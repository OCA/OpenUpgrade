# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_procurement_fields(env):
    # Update new field created_purchase_line_id at stock.move
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET created_purchase_line_id = po.purchase_line_id
        FROM procurement_order po
        WHERE sm.procurement_id = po.id
            AND po.purchase_line_id IS NOT NULL"""
    )
    # Update new field orderpoint_id at purchase.order.line
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET orderpoint_id = po.orderpoint_id
        FROM procurement_order po
        WHERE pol.id = po.purchase_line_id
            AND po.orderpoint_id IS NOT NULL"""
    )


@openupgrade.logging()
def fill_purchase_order_picking_fields(env):
    """Fill computed stored fields through SQL for performance."""
    # Field picking_ids
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO purchase_order_stock_picking_rel
        (purchase_order_id, stock_picking_id)
        SELECT order_id, picking_id
        FROM purchase_order_line pol,
            stock_move sm
        WHERE sm.purchase_line_id = pol.id
            AND sm.picking_id IS NOT NULL
        GROUP BY pol.order_id, sm.picking_id""",
    )
    # First we set everything to 0 for picking_count
    openupgrade.logged_query(
        env.cr, "UPDATE purchase_order po SET picking_count = 0",
    )
    # Now we set actual values for picking_count
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order po
        SET picking_count = sub.picking_count
        FROM (
            SELECT purchase_order_id AS id,
                COUNT(stock_picking_id) AS picking_count
            FROM purchase_order_stock_picking_rel
            GROUP BY purchase_order_id
        ) AS sub
        WHERE sub.id = po.id""",
    )
    # Field invoice_ids
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_invoice_purchase_order_rel
        (purchase_order_id, account_invoice_id)
        SELECT order_id, invoice_id
        FROM purchase_order_line pol,
            account_invoice_line ail
        WHERE ail.purchase_line_id = pol.id
        GROUP BY pol.order_id, ail.invoice_id""",
    )
    # First we set everything to 0 for invoice_count
    openupgrade.logged_query(
        env.cr, "UPDATE purchase_order po SET invoice_count = 0",
    )
    # Now we set actual values for invoice_count
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order po
        SET invoice_count = sub.invoice_count
        FROM (
            SELECT purchase_order_id AS id,
                COUNT(account_invoice_id) AS invoice_count
            FROM account_invoice_purchase_order_rel
            GROUP BY purchase_order_id
        ) AS sub
        WHERE sub.id = po.id""",
    )


def activate_vendor_pricelists(env):
    """If module `product_by_supplier` (OCA/purchase-workflow) was installed we
    need to activate the "Vendor Pricelists" setting as the module was
    deprecated in favour of it."""
    env.cr.execute(
        """
        SELECT id
        FROM ir_model_data
        WHERE module = 'purchase' AND
            name = 'view_product_supplierinfo_search'
        """
    )
    if env.cr.fetchone():
        employee_group = env.ref('base.module_category_human_resources')
        vendor_price_group = env.ref('purchase.group_manage_vendor_price')
        employee_group.write({'implied_ids': [(4, vendor_price_group.id)]})


@openupgrade.migrate()
def migrate(env, version):
    update_procurement_fields(env)
    fill_purchase_order_picking_fields(env)
    openupgrade.load_data(
        env.cr, 'purchase', 'migrations/11.0.1.2/noupdate_changes.xml',
    )
    activate_vendor_pricelists(env)
