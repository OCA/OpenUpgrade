# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def move_fields_from_invoice_to_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET purchase_line_id = ail.purchase_line_id
        FROM account_invoice_line ail
        WHERE aml.old_invoice_line_id = ail.id AND
            ail.purchase_line_id IS NOT NULL"""
    )


def change_type_purchase_order_date_approve(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order
        SET date_approve = {date}::TIMESTAMP AT TIME ZONE 'UTC'
        WHERE {date} IS NOT NULL
        """.format(date=openupgrade.get_legacy_name('date_approve'))
    )


def fill_account_move_purchase_order_rel_table(env):
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_purchase_order_rel (
            purchase_order_id, account_move_id)
        SELECT rel.purchase_order_id, am.id
        FROM account_invoice_purchase_order_rel rel
        JOIN account_invoice ai ON rel.account_invoice_id = ai.id
        JOIN account_move am ON am.old_invoice_id = ai.id
        ON CONFLICT DO NOTHING"""
    )


def fill_purchase_order_line_qty_received_method(cr):
    if openupgrade.column_exists(cr, 'purchase_order', 'picking_type_id'):
        # purchase_stock is installed
        # set qty_delivered_method = 'stock_moves'
        openupgrade.logged_query(
            cr, """
            UPDATE purchase_order_line pol
            SET qty_received_method = 'stock_moves', qty_received_manual = NULL
            FROM product_product pp
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE pol.product_id = pp.id AND pol.display_type IS NULL
                AND pt.type IN ('consu', 'product')"""
        )
    # set qty_received_method = 'manual'
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_order_line pol
        SET qty_received_method = 'manual'
        FROM product_product pp
        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pol.qty_received_method IS NULL AND pol.product_id = pp.id
            AND pt.type IN ('consu', 'service')"""
    )


@openupgrade.migrate()
def migrate(env, version):
    move_fields_from_invoice_to_moves(env)
    change_type_purchase_order_date_approve(env)
    fill_account_move_purchase_order_rel_table(env)
    fill_purchase_order_line_qty_received_method(env.cr)
    openupgrade.load_data(
        env.cr, "purchase", "migrations/13.0.1.2/noupdate_changes.xml")
