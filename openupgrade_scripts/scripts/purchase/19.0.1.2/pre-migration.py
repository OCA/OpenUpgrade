# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

renamed_fields = [
    ("purchase.order", "purchase_order", "notes", "note"),
    ("purchase.order.line", "purchase_order_line", "product_uom", "product_uom_id"),
    ("purchase.order.line", "purchase_order_line", "taxes_id", "tax_ids"),
]

added_fields = [
    ("locked", "purchase.order", "purchase_order", "boolean", None, "purchase", False),
    (
        "technical_price_unit",
        "purchase.order.line",
        "purchase_order_line",
        "float",
        None,
        "purchase",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, renamed_fields)
    openupgrade.add_fields(env, added_fields)
