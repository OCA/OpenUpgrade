# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_stock_picking_type_default_locations(env):
    picking_types = env["stock.picking.type"].search(
        [("default_location_src_id", "=", False)]
    )
    picking_types._compute_default_location_src_id()
    picking_types = env["stock.picking.type"].search(
        [("default_location_dest_id", "=", False)]
    )
    picking_types._compute_default_location_dest_id()


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_picking_type_default_locations(env)
