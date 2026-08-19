# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    migrate_dock_locations(env)
    set_dispatch_management(env)


def migrate_dock_locations(env):
    """Link legacy is_a_dock locations to outgoing picking types as dock_ids."""
    legacy_is_a_dock = openupgrade.get_legacy_name("is_a_dock")
    env.cr.execute(
        f"""
        INSERT INTO dock_location_stock_picking_type_rel (
            stock_picking_type_id, stock_location_id
        )
        SELECT spt.id, sl.id
        FROM stock_location sl
        JOIN stock_picking_type spt
          ON spt.warehouse_id = sl.warehouse_id
         AND spt.code = 'outgoing'
        WHERE sl.{legacy_is_a_dock}
        """
    )


def set_dispatch_management(env):
    """Enable dispatch_management on picking types that need it,
    matching stock_warehouse._get_picking_type_update_values defaults."""
    env.cr.execute(
        """
        UPDATE stock_picking_type spt
        SET dispatch_management = TRUE
        FROM stock_warehouse sw
        WHERE spt.warehouse_id = sw.id
          AND (
              spt.code IN ('incoming', 'outgoing')
              OR (sw.delivery_steps = 'pick_pack_ship' AND spt.id = sw.pack_type_id)
              OR (sw.delivery_steps = 'pick_ship' AND spt.id = sw.pick_type_id)
          )
        """
    )
