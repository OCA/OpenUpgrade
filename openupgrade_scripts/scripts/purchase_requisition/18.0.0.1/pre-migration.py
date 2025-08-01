# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_new_columns = [
    ("purchase.order.line", "price_total_cc", "float"),
    ("purchase.requisition", "requisition_type", "selection"),
]
field_renames = [
    ("purchase.requisition", "purchase_requisition", "origin", "reference"),
    ("purchase.requisition", "purchase_requisition", "schedule_date", "date_start"),
]


def fill_purchase_order_line_price_total_cc(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order_line pol
        SET price_total_cc = COALESCE(
            pol.price_subtotal / NULLIF(po.currency_rate, 0),
            0
        )
        FROM purchase_order po
        WHERE po.id = pol.order_id
        """,
    )


def fill_purchase_requisition_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_requisition pr
        SET requisition_type = CASE
            WHEN prt.quantity_copy = 'none' THEN 'blanket_order'
            ELSE 'purchase_template' END
        FROM purchase_requisition_type prt
        WHERE prt.id = pr.type_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version=None):
    openupgrade.copy_columns(
        env.cr,
        {"purchase_requisition": [("state", None, None)]},
    )
    openupgrade.add_columns(env, _new_columns)
    openupgrade.rename_fields(env, field_renames)
    fill_purchase_order_line_price_total_cc(env)
    fill_purchase_requisition_type(env)
    old_column = openupgrade.get_legacy_name("state")
    openupgrade.map_values(
        env.cr,
        old_column,
        "state",
        [("in_progress", "confirmed"), ("ongoing", "confirmed"), ("open", "confirmed")],
        table="purchase_requisition",
    )
    openupgrade.remove_tables_fks(env.cr, ["purchase_requisition_type"])
