# -*- coding: utf-8 -*-
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def copy_global_rules(env):
    """Copy global rules to another table and remove them from main one."""
    for table in ['procurement_rule', 'stock_location_path']:
        openupgrade.logged_query(
            env.cr, """
            CREATE TABLE %s AS (
                SELECT * FROM %s
                WHERE route_id IS NULL
            )""" % (openupgrade.get_legacy_name(table), table)
        )
        openupgrade.logged_query(
            env.cr, "DELETE FROM %s WHERE route_id IS NULL" % table,
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


def drop_slow_constraint(env):
    """Removing this constraint, that doesn't affect new data structure, as
    it belongs to an obsolete model, we get tons of more performance on
    quant removal.
    """
    openupgrade.logged_query(
        env.cr, "ALTER TABLE stock_move_operation_link DROP CONSTRAINT "
                "stock_move_operation_link_reserved_quant_id_fkey",
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    copy_global_rules(env)
    delete_quants_for_consumable(env)
    drop_slow_constraint(env)
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
