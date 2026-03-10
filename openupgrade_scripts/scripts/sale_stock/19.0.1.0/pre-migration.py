# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_renamed_field_references = [
    (
        "stock.reference",
        "sale_id",
        "sale_ids",
    ),
    (
        "sale.order",
        "procurement_group_id",
        "stock_reference_ids",
    ),
    (
        "sale.order.line",
        "route_id",
        "route_ids",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_field_references(env, _renamed_field_references)
