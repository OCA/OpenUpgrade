# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tools import float_compare
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


@openupgrade.logging()
def compute_stock_move_reference(env):
    """Compute through SQL this field for saving time."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move
        SET reference = name
        WHERE picking_id IS NULL"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET reference = sp.name
        FROM stock_picking sp
        WHERE sm.picking_id = sp.id"""
    )


@openupgrade.logging()
def compute_picking_scheduled_date(env):
    """Compute through SQL this field for saving time."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_picking sp
        SET scheduled_date = sub.date_expected
        FROM (
            SELECT sm.picking_id,
                CASE WHEN sp.move_type = 'direct'
                THEN MIN(sm.date_expected)
                ELSE MAX(sm.date_expected)
                END AS date_expected
            FROM stock_move sm, stock_picking sp
            WHERE sm.picking_id = sp.id
            GROUP BY sm.picking_id, sp.move_type
        ) AS sub
        WHERE sub.picking_id = sp.id"""
    )


@openupgrade.logging()
def product_assign_responsible(env):
    """Assign as responsible the creator of the product."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template
        SET responsible_id = COALESCE(create_uid, 1)
        """
    )


@openupgrade.logging()
def create_specific_procurement_rules_from_globals(env):
    """Create one record per route for the global rules found in previous
    version.
    """
    for table in ['procurement_rule', 'stock_location_path']:
        env.cr.execute(
            """SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
                AND column_name != 'id'
            ORDER BY ordinal_position""",
            (table, ),
        )
        dest_columns = [x[0] for x in env.cr.fetchall()]
        src_columns = [
            ('t.' + x) if x != 'route_id' else 'slr.id' for x in dest_columns
        ]
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO %s
            (%s)
            SELECT %s
            FROM %s t, stock_location_route slr""", (
                AsIs(table),
                AsIs(", ".join(dest_columns)),
                AsIs(", ".join(src_columns)),
                AsIs(openupgrade.get_legacy_name(table)),
            ),
        )


@openupgrade.logging()
def set_quant_reserved_qty(env):
    """If there was a reserved move, then the entire quantity was reserved,
    so we have to put quant qty as the reserved qty. Later on end migration,
    merge operation will sum all the reserved ones.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_quant
        SET reserved_quantity = quantity
        WHERE reservation_id IS NOT NULL""",
    )


@openupgrade.logging()
def set_partially_available_state(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move
        SET state = 'partially_available'
        WHERE partially_available AND state != 'done'"""
    )


@openupgrade.logging()
def create_stock_move_line(env):
    """This method creates stock.move.line recreated from old
    stock.pack.operation records. These records are created only for done
    moves, as for those not done, it's handled later:

    * For outgoing or internal transfers without reserved quantity, clicking on
      "Check availability" will work.
    * For outgoing or internal transfers with reserved quantity,
      stock.move.line records are created from other source (quants) later
      in `create_stock_move_line_reserved` method.
    * For incoming transfers not yet validated, they are created later.

    Information is taken from stock.move.operation.link instead of
    stock.pack.operation/stock.operation.lot as v10 grouped together several
    stock.move lines with the same product in the same operation record, making
    impossible to split the lot quantity across each move.
    """
    # If coming from v8, chances of having stock_move_operation_link (smol)
    # `reserved_quant_id` filled are low, so `lot_id` will remain empty on
    # created sml on lot of cases. As in v8 there's no stock.pack.operation
    # (spo)>stock.pack.operation.lot structure, we can use lot informed in spo
    lot_column = 'openupgrade_legacy_9_0_lot_id'
    if openupgrade.column_exists(env.cr, 'stock_pack_operation', lot_column):
        lot_expr = "COALESCE(sq.lot_id, %s)" % lot_column
    else:
        lot_expr = 'sq.lot_id'
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_move_line (
            create_date,
            create_uid,
            date,
            location_dest_id,
            location_id,
            lot_id,
            lot_name,
            move_id,
            ordered_qty,
            owner_id,
            package_id,
            picking_id,
            product_id,
            product_qty,
            product_uom_id,
            product_uom_qty,
            qty_done,
            reference,
            state,
            result_package_id,
            write_date,
            write_uid
        )
        SELECT
            spo.create_date,
            spo.create_uid,
            spo.date,
            spo.location_dest_id,
            spo.location_id,
            %s,
            spl.name,
            sm.id,
            smol.qty,
            spo.owner_id,
            spo.package_id,
            spo.picking_id,
            spo.product_id,
            smol.qty,
            spo.product_uom_id,
            smol.qty,
            smol.qty,
            COALESCE(sp.name, sm.name),
            'done',
            spo.result_package_id,
            spo.write_date,
            spo.write_uid
        FROM stock_pack_operation spo
            INNER JOIN stock_move_operation_link smol
                ON smol.operation_id = spo.id
            INNER JOIN stock_move sm ON sm.id = smol.move_id
            INNER JOIN product_product pp ON spo.product_id = pp.id
            LEFT JOIN stock_picking sp ON sp.id = spo.picking_id
            LEFT JOIN stock_quant sq ON sq.id = smol.reserved_quant_id
            LEFT JOIN stock_production_lot spl ON spl.id = sq.lot_id
        WHERE sm.state = 'done'
        """, (AsIs(lot_expr), ),
    )


@openupgrade.logging()
def fill_missing_lots_for_sml(env):
    """On v10, `reserved_quant_id` field on stock.move.operation.link is
    filled unless manual operations or extra quantities are added on transfer
    wizard, which technically means that they fall under this part of code:

    https://github.com/OCA/OpenUpgrade/blob/
    a0890c2bcfee62bdf9daf89e267d01b25a55d793/addons/stock/models/
    stock_picking.py#L759

    The SQL query for inserting stock.move.line can't be modified as explained
    in previous method, so we call this method afterwards for filling missing
    lots when possible.

    Heuristic:

    * Find stock.move.operation.link records without reserved quant, but the
      linked operation has some lots.
    * Check the stock.move.line (sml) new records associated to the move. If
      there's only one sml with the same quantity of stock.pack.operation.
    * If found, then we can conclude the lot is that one.
    * If not, we try to see that all the stock.move.line of the same product
      makes the total of the stock.pack.operation.lot for concluding the same.
    """
    env.cr.execute(
        """SELECT sm.id, spol.qty, spol.lot_id, spol.lot_name
        FROM stock_pack_operation spo
            JOIN stock_move_operation_link smol
                ON smol.operation_id = spo.id
            JOIN stock_move sm ON sm.id = smol.move_id
            JOIN stock_pack_operation_lot spol
                ON spol.operation_id = spo.id
        WHERE smol.reserved_quant_id IS NULL""",
    )
    rounding = env['decimal.precision'].precision_get(
        'Product Unit of Measure')
    Move = env['stock.move']
    for row in env.cr.fetchall():
        move = Move.browse(row[0])
        smls = move.move_line_ids.filtered(lambda x: (float_compare(
            x.product_qty, row[1], precision_digits=rounding
        ) == 0))
        match = len(smls) == 1
        if not match:
            smls = move.picking_id.mapped('move_line_ids').filtered(
                lambda x: x.product_id == move.move_line_ids[:1].product_id)
            match = float_compare(
                sum(smls.mapped('product_qty')), row[1],
                precision_digits=rounding,
            ) == 0
        if match and smls:
            # Done through SQL for avoiding triggering other changes
            env.cr.execute(
                """UPDATE stock_move_line
                SET lot_id = %s, lot_name = %s
                WHERE id IN %s""",
                (row[2], row[3], tuple(smls.ids)),
            )


@openupgrade.logging()
def create_stock_move_line_incoming(env):
    """This method creates stock.move.line for incoming moves that are not yet
    validated and don't come from a return (as these need reservation the
    same as the deliveries).

    The drawback of current method is that any lot/package already input, but
    not validated, will be lost. Maybe we can recreate this through
    stock_move_operation_link the same as done moves.
    """
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_move_line (
            create_date,
            create_uid,
            date,
            location_dest_id,
            location_id,
            move_id,
            ordered_qty,
            picking_id,
            product_id,
            product_qty,
            product_uom_id,
            product_uom_qty,
            reference,
            state,
            write_date,
            write_uid
        )
        SELECT
            sm.create_date,
            sm.create_uid,
            sm.date,
            sm.location_dest_id,
            sm.location_id,
            sm.id,
            sm.product_uom_qty,
            sp.id,
            sm.product_id,
            sm.product_qty,
            sm.product_uom,
            sm.product_uom_qty,
            COALESCE(sp.name, sm.name),
            'assigned',
            sm.write_date,
            sm.write_uid
        FROM stock_move sm
            INNER JOIN stock_picking sp ON sp.id = sm.picking_id
            INNER JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
        WHERE sm.state = 'assigned'
            AND sm.origin_returned_move_id IS NULL
            AND spt.code = 'incoming'
        """,
    )


@openupgrade.logging()
def create_stock_move_line_reserved(env):
    """This method creates stock.move.line got from old stock.quant
    reservation_id field for recreating partially available moves.

    TODO: Check this with multiple UoMs.
    """
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_move_line (
            create_date,
            create_uid,
            date,
            location_dest_id,
            location_id,
            lot_id,
            lot_name,
            move_id,
            ordered_qty,
            owner_id,
            package_id,
            picking_id,
            product_id,
            product_qty,
            product_uom_id,
            product_uom_qty,
            qty_done,
            reference,
            state,
            write_date,
            write_uid
        )
        SELECT
            current_timestamp,
            MIN(sq.write_uid),
            sm.date,
            sm.location_dest_id,
            sq.location_id,
            sq.lot_id,
            MIN(spl.name),
            sm.id,
            LEAST(SUM(sq.quantity), sm.product_uom_qty),
            sq.owner_id,
            sq.package_id,
            sm.picking_id,
            sq.product_id,
            LEAST(SUM(sq.quantity), sm.product_uom_qty),
            sm.product_uom,
            LEAST(SUM(sq.quantity), sm.product_uom_qty),
            0,
            MIN(COALESCE(sp.name, sm.name)),
            sm.state,
            current_timestamp,
            MIN(sq.write_uid)
        FROM stock_quant sq
            INNER JOIN stock_move sm ON sm.id = sq.reservation_id
            LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
            LEFT JOIN stock_production_lot spl ON spl.id = sq.lot_id
        GROUP BY sq.lot_id, sq.product_id, sq.owner_id, sq.package_id,
            sq.location_id, sm.id""",
    )


@openupgrade.logging()
def create_stock_move_line_from_inventory_moves(env):
    """This method creates stock.move.line got from inventory moves.
    """
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_move_line (
            create_date,
            create_uid,
            date,
            location_dest_id,
            location_id,
            lot_id,
            lot_name,
            move_id,
            ordered_qty,
            owner_id,
            picking_id,
            product_id,
            product_qty,
            product_uom_id,
            product_uom_qty,
            qty_done,
            reference,
            state,
            write_date,
            write_uid
        )
        SELECT
            sm.create_date,
            sm.create_uid,
            sm.date,
            sm.location_dest_id,
            sm.location_id,
            spl.id,
            spl.name,
            sm.id,
            0,
            sm.restrict_partner_id,
            NULL,
            sm.product_id,
            0,
            sm.product_uom,
            0,
            sm.product_uom_qty,
            sm.name,
            sm.state,
            sm.write_date,
            sm.write_uid
        FROM stock_move sm
        INNER JOIN stock_inventory si ON sm.inventory_id = si.id
        LEFT JOIN (SELECT sqmr.move_id, MIN(sq.lot_id) AS lot_id
                   FROM stock_quant_move_rel sqmr
                   LEFT JOIN stock_quant sq ON sqmr.quant_id = sq.id
                   WHERE sq.lot_id IS NOT NULL
                   GROUP BY move_id
        ) AS move_lot_rel ON move_lot_rel.move_id = sm.id
        LEFT JOIN stock_production_lot spl ON move_lot_rel.lot_id = spl.id
        WHERE si.state = 'done' AND sm.state = 'done'
        """,
    )


def recompute_stock_move_line_qty_different_uom(env):
    """Re-compute product_qty for those lines where product UoM != line UoM."""
    env.cr.execute(
        """SELECT sml.id
        FROM stock_move_line sml
            INNER JOIN product_product pp ON pp.id = sml.product_id
            INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE pt.uom_id != sml.product_uom_id"""
    )
    lines = env['stock.move.line'].browse([x[0] for x in env.cr.fetchall()])
    for line in lines:
        try:  # Don't fail on incompatible conversions
            product_qty = line.product_uom_id._compute_quantity(
                line.product_uom_qty, line.product_id.uom_id,
                rounding_method='HALF-UP',
            )
            # Can't assign by ORM, so by SQL
            env.cr.execute(
                "UPDATE stock_move_line SET product_qty = %s WHERE id = %s",
                (product_qty, line.id),
            )
        except UserError:
            pass


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    compute_stock_move_reference(env)
    compute_picking_scheduled_date(env)
    product_assign_responsible(env)
    create_specific_procurement_rules_from_globals(env)
    set_quant_reserved_qty(env)
    openupgrade.m2o_to_x2m(
        env.cr, env['stock.move'], 'stock_move', 'move_dest_ids',
        'move_dest_id',
    )
    # TODO: Get is_initial_demand_editable, is_locked values in stock.move
    set_partially_available_state(env)
    create_stock_move_line(env)
    fill_missing_lots_for_sml(env)
    create_stock_move_line_incoming(env)
    create_stock_move_line_reserved(env)
    create_stock_move_line_from_inventory_moves(env)
    recompute_stock_move_line_qty_different_uom(env)
    openupgrade.load_data(
        env.cr, 'stock', 'migrations/11.0.1.1/noupdate_changes.xml',
    )
