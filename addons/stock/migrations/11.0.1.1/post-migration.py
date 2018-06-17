# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def product_assign_responsible(env):
    """Assign as responsible the creator of the product."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template
        SET responsible_id = create_uid
        """
    )


def create_specific_procurement_rules_from_globals(env):
    """Create one record per route for the global rules found in previous
    version.
    """
    for table in ['procurement_rule', 'stock_location_path']:
        env.cr.execute(
            """SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position""",
            (table, ),
        )
        columns = [
            ('t.' + x[0]) if x != 'route_id' else 'slr.id'
            for x in env.cr.fetchall()
        ]
        openupgrade.logged_query(
            env.cr, """
            INSERT INTO %s
            SELECT %s
            FROM %s t, stock_location_route slr
            """ % (
                table,
                ", ".join(columns),
                openupgrade.get_legacy_name(table)
            ),
        )


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


def set_partially_available_state(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move
        SET state = 'partially_available'
        WHERE partially_available AND state='waiting'"""
    )


def create_stock_move_line(env):
    """This method creates stock.move.line recreated from old
    stock.pack.operation records.
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
            COALESCE(spol.lot_id, sm.restrict_lot_id),
            spol.lot_name,
            sm.id,
            spo.ordered_qty,
            spo.owner_id,
            spo.package_id,
            spo.picking_id,
            spo.product_id,
            spo.product_qty,
            spo.product_uom_id,
            spo.product_qty,
            spo.qty_done,
            COALESCE(sp.name, sm.name),
            spo.result_package_id,
            spo.write_date,
            spo.write_uid
        FROM stock_pack_operation spo
            INNER JOIN stock_move_operation_link smol
                ON smol.operation_id = spo.id
            INNER JOIN stock_move sm ON sm.id = smol.move_id
            INNER JOIN product_product pp ON spo.product_id = pp.id
            LEFT JOIN stock_picking sp ON sp.id = spo.picking_id
            LEFT JOIN stock_pack_operation_lot spol
                ON spol.operation_id = spo.id
        """
    )
    # Re-compute product_qty for those lines where product UoM != line UoM
    env.cr.execute(
        """SELECT sml.id
        FROM stock_move_line sml
            INNER JOIN product_product pp ON pp.id = sml.product_id
            INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE pt.uom_id != sml.product_uom_id"""
    )
    lines = env['stock.move.line'].browse([x[0] for x in env.cr.fetchall()])
    for line in lines:
        product_qty = line.product_uom_id._compute_quantity(
            line.product_uom_qty, line.product_id.uom_id,
            rounding_method='HALF-UP',
        )
        # Can't assign by ORM, so by SQL
        env.cr.execute(
            "UPDATE stock_move_line SET product_qty = %s WHERE id = %s",
            (product_qty, line.id),
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
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
