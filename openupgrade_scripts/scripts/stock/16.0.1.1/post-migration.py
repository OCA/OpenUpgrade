# Copyright (C) 2023-Today GRAP (http://www.grap.coop)
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade


def handle_stock_picking_backorder_strategy(env):
    # Handle the merge of OCA/stock-logistics-workflow/stock_picking_backorder_strategy
    # feature in odoo/stock V16 module.
    if openupgrade.column_exists(
        env.cr, "stock_picking_type", openupgrade.get_legacy_name("backorder_strategy")
    ):
        openupgrade.map_values(
            env.cr,
            openupgrade.get_legacy_name("backorder_strategy"),
            "create_backorder",
            [
                ("manual", "ask"),
                ("create", "always"),
                ("no_create", "never"),
                ("cancel", "never"),
            ],
            table="stock_picking_type",
        )


@openupgrade.migrate()
def migrate(env, version):
    handle_stock_picking_backorder_strategy(env)
