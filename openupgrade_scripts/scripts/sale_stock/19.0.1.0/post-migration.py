# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "sale_stock", "19.0.1.0/noupdate_changes.xml")
    openupgrade.m2o_to_x2m(
        env.cr,
        env["sale.order"],
        "sale_order",
        "stock_reference_ids",
        "procurement_group_id",
    )
    openupgrade.m2o_to_x2m(
        env.cr, env["sale.order.line"], "sale_order_line", "route_ids", "route_id"
    )
