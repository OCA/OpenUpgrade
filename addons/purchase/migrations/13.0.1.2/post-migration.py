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
        UPDATE purchase_order po
        SET date_approve = mm.date
        FROM mail_message mm
        WHERE mm.subtype_id = %s
            AND mm.model = 'purchase.order'
            AND mm.res_id = po.id""",
        (env.ref('purchase.mt_rfq_approved').id, ),
    )


def fill_account_move_purchase_order_rel_table(env):
    # Remove temp table and re-create m2m table through ORM method
    openupgrade.logged_query(env.cr, "DROP TABLE account_move_purchase_order_rel")
    Move = env["purchase.order"]
    Move._fields["invoice_ids"].update_db(Move, False)
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_move_purchase_order_rel (
            purchase_order_id, account_move_id)
        SELECT rel.purchase_order_id, am.id
        FROM account_invoice_purchase_order_rel rel
        JOIN account_move am ON am.old_invoice_id = rel.account_invoice_id
        ON CONFLICT DO NOTHING"""
    )


def fill_purchase_order_line_qty_received_method(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE purchase_order_line pol
        SET qty_received_method = 'manual'
        FROM product_product pp
        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pol.product_id = pp.id
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
