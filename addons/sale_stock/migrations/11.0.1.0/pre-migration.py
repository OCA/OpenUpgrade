# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_procurement_field_from_sale(env):
    """Connecting new sale_id field of procurement_group with respective
    sale orders (considering procurement_group_id of sale order).
    """
    if not openupgrade.column_exists(env.cr, 'procurement_group', 'sale_id'):
        openupgrade.add_fields(env, [
            ('sale_id', 'procurement.group', 'procurement_group', 'many2one',
             False, 'sale_stock'),
        ])
    openupgrade.logged_query(
        env.cr, """
        UPDATE procurement_group pg
        SET sale_id = sol.order_id
        FROM stock_move sm
        INNER JOIN sale_order_line sol ON sm.sale_line_id = sol.id
        WHERE sm.group_id = pg.id""",
    )


def update_picking_sale_related(env):
    """This field is a related one from procurement group."""
    if not openupgrade.column_exists(env.cr, 'stock_picking', 'sale_id'):
        openupgrade.logged_query(
            env.cr, "ALTER TABLE stock_picking ADD sale_id int4",
        )
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_picking sp
        SET sale_id = pg.sale_id
        FROM procurement_group pg
        WHERE sp.group_id = pg.id
            AND pg.sale_id IS NOT NULL""",
    )


def update_stock_move_field_from_procurement_order(env):
    """Filling the values of new sale_order_id field of stock_move
    with respective values of old procurement_order
    """
    if not openupgrade.column_exists(env.cr, 'stock_move', 'sale_line_id'):
        openupgrade.add_fields(env, [
            ('sale_line_id', 'stock.move', 'stock_move', 'many2one',
             False, 'sale_stock'),
        ])
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET sale_line_id = po.sale_line_id
        FROM procurement_order po
        WHERE sm.procurement_id = po.id
            AND po.sale_line_id IS NOT NULL""",
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_stock_move_field_from_procurement_order(env)
    update_procurement_field_from_sale(env)
    update_picking_sale_related(env)
