# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _stock_scrap_convert_move_id_m2o_to_o2m(env):
    """
    Convert m2o to o2m in 'stock.scrap'
    """
    openupgrade.m2o_to_x2m(
        env.cr, env["stock.scrap"], "stock_scrap", "move_ids", "move_id"
    )


def fix_move_quantity(env):
    """
    Recompute move quantity for move lines that have been changed in pre-migration
    """
    env.cr.execute(
        """
        SELECT DISTINCT move_id FROM stock_move_line
        WHERE
        state IN ('assigned', 'partially_available')
        AND reserved_qty <> 0
        """
    )
    moves = env["stock.move"].browse(_id for (_id,) in env.cr.fetchall())
    env.add_to_compute(moves._fields["quantity"], moves)
    moves._recompute_recordset(["quantity"])


def link_returned_pickings(env):
    """
    Link pickings containing returned moves to the pickings containing the moves
    being returned
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking
        SET
        return_id = returned_move.picking_id
        FROM
        stock_move
        JOIN stock_move returned_move
        ON stock_move.origin_returned_move_id = returned_move.id
        WHERE
        stock_move.picking_id = stock_picking.id
        """,
    )


def set_picking_type_return_location(env):
    """
    Set default_location_return_id on picking types from the destination location
    of the warehouse's return picking type
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_picking_type
        SET
        default_location_return_id = COALESCE(
            picking_return_type.default_location_dest_id,
            warehouse_return_type.default_location_dest_id
        )
        FROM
        stock_picking_type self
        JOIN stock_warehouse
        ON self.warehouse_id=stock_warehouse.id
        LEFT JOIN stock_picking_type picking_return_type
        ON self.return_picking_type_id=picking_return_type.id
        LEFT JOIN stock_picking_type warehouse_return_type
        ON stock_warehouse.return_type_id=warehouse_return_type.id
        WHERE
        stock_picking_type.id=self.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "stock", "17.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "stock", ["mail_template_data_delivery_confirmation"]
    )
    _stock_scrap_convert_move_id_m2o_to_o2m(env)
    fix_move_quantity(env)
    link_returned_pickings(env)
    set_picking_type_return_location(env)
