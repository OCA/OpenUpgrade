# -*- coding: utf-8 -*-
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def _get_dummy_route_id(env, default):
    """ Return an inactive dummy route. Create on demand """
    if default:
        return default
    env.cr.execute(
        """ INSERT INTO stock_location_route
        (create_date, create_uid, name, active)
        VALUES(now() at time zone 'UTC', 1,
        'OpenUpgrade 11.0 Dummy Route for inactive rules & paths',
        False) RETURNING id """)
    return env.cr.fetchone()[0]


@openupgrade.logging()
def create_specific_procurement_rules_from_globals(env):
    """Procurement rules and location paths without a route were considered
    global in Odoo 10. Now that the route_id is a required field in both
    tables, expand active rules and paths without a route so that we will end
    up with one record for each route. Don't expand inactive records or expand
    records for inactive routes. If necessary, create a dummy inactive route
    to assign to inactive records without a route.

    Note that rules and paths are left dangling if you unlink their route.
    Before starting the migration, check to see which of your 'global'
    rules need to be set to inactive to prevent the unexpected expansion
    of such rules and paths.
    """
    dummy_route_id = False
    # Pick an arbitrary active route to assign to dangling records.
    # New records will be created down below for all other routes.
    env.cr.execute(
        "SELECT id FROM stock_location_route WHERE active LIMIT 1")
    row = env.cr.fetchone()
    first_route_id = (
        row[0] if row else _get_dummy_route_id(env, dummy_route_id))

    for table in ['procurement_rule', 'stock_location_path']:
        openupgrade.logged_query(
            env.cr, """
            CREATE TABLE %s AS (
                SELECT * FROM %s
                WHERE route_id IS NULL
            )
            """, (AsIs(openupgrade.get_legacy_name(table)), AsIs(table)))

        # Check for inactive items
        env.cr.execute(
            """SELECT COUNT(*) FROM %s
            WHERE route_id IS NULL AND active IS NOT TRUE""",
            (AsIs(table),))
        res = env.cr.fetchone()
        if res[0]:
            dummy_route_id = _get_dummy_route_id(env, dummy_route_id)
            openupgrade.logged_query(
                env.cr,
                """UPDATE %s SET route_id = %s
                WHERE route_id IS NULL AND active IS NOT TRUE""",
                (AsIs(table), dummy_route_id))

        # Assign the first route to the original dangling records
        openupgrade.logged_query(
            env.cr, """
            UPDATE %s
            SET route_id = %s WHERE route_id IS NULL """, (
                AsIs(table),
                first_route_id,
            ),
        )

        # Perform the expansion, creating copies for all other routes
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
            FROM %s t, stock_location_route slr
            WHERE t.route_id IS NULL AND t.active
            AND slr.active AND slr.id != %s """, (
                AsIs(table),
                AsIs(", ".join(dest_columns)),
                AsIs(", ".join(src_columns)),
                AsIs(openupgrade.get_legacy_name(table)),
                first_route_id,
            ),
        )


def delete_quants_for_consumable(env):
    """On v11, consumable products don't generate quants, so we can remove them
    as soon as possible for cleaning the DB and avoid other computations (like
    the merge records operation).
    """
    openupgrade.logged_query(
        env.cr, """
        DELETE FROM stock_quant sq
        USING product_product pp,
            product_template pt
        WHERE sq.product_id = pp.id
            AND pt.id = pp.product_tmpl_id
            AND pt.type = 'consu'
        """
    )


def fix_act_window(env):
    """Action window with XML-ID 'stock.action_procurement_compute' has
    set src_model='procurement.order', and this will provoke an error as
    new definition doesn't overwrite this field. We empty that value before
    that happens. The source of this assignation is not clear, but it doesn't
    hurt any way.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_act_window iaw
        SET src_model = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = iaw.id
            AND imd.module = 'stock'
            AND imd.name = 'action_procurement_compute'""",
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    create_specific_procurement_rules_from_globals(env)
    delete_quants_for_consumable(env)
    fix_act_window(env)
    openupgrade.update_module_moved_fields(
        env.cr, 'stock.move', ['has_tracking'], 'mrp', 'stock',
    )
    openupgrade.update_module_moved_fields(
        env.cr, 'stock.move', ['quantity_done'], 'mrp', 'stock',
    )
    openupgrade.rename_fields(
        env, [
            ('stock.quant', 'stock_quant', 'qty', 'quantity'),
        ]
    )
    openupgrade.copy_columns(
        env.cr, {
            'stock_picking': [
                ('state', None, None),
            ],
        },
    )
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('state'), 'state',
        [('partially_available', 'assigned')], table='stock_picking',
    )
    openupgrade.add_fields(
        env, [
            ('reference', 'stock.move', 'stock_move', 'char', False, 'stock'),
            ('scheduled_date', 'stock.picking', 'stock_picking', 'date', False,
             'stock'),
        ],
    )
    openupgrade.set_xml_ids_noupdate_value(
        env, 'stock', [
            'barcode_rule_location',
            'barcode_rule_lot',
            'barcode_rule_package',
            'barcode_rule_weight_three_dec',
        ], True)
