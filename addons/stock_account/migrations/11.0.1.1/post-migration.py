# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_stock_move_id_for_account_moves(env):
    """In v10 journal items are created with the name of the stock moves,
    together with date and product_id,
    they are the best information we have to find the originating stock move
    of a journal entry."""
    openupgrade.logger.info(
        "Compute account_move_ids for stock.move. (Incoming)")
    # incoming stock moves that likely generated a account.move:
    env.cr.execute("""
        SELECT sm.id, sm.product_id, sm.name, sm.date
        FROM stock_move sm
        INNER JOIN stock_location loc_from
        ON sm.location_id = loc_from.id
        INNER JOIN stock_location loc_to
        ON sm.location_dest_id = loc_to.id
        WHERE (loc_from.company_id IS NULL
                OR loc_from.usage <> 'internal')
            AND (loc_to.company_id IS NOT NULL
                OR loc_from.usage = 'internal')
            AND sm.state = 'done'
    """)
    for move, product, move_name, move_date in env.cr.fetchall():
        # TODO: use am creating date and truncate in hours or minutes?
        # sm date is changed when done and the am is created then.
        env.cr.execute("""
            SELECT DISTINCT am.id
            FROM account_move_line aml
            INNER JOIN account_move am
            ON aml.move_id = am.id
            WHERE aml.product_id = %s
                AND aml.name = %s
                AND DATE_TRUNC('day', am.date) = to_date(%s, 'YYYY/MM/DD')
        """, (product, move_name, move_date))
        for am in env.cr.fetchall():
            openupgrade.logger.debug("%s" % move_date)
            env.cr.execute("""
                UPDATE account_move
                SET stock_move_id = %s
                WHERE id = %s
            """, (move, am))

    # Outgoing
    openupgrade.logger.info(
        "Compute account_move_ids for stock.move. (Outgoing)")
    env.cr.execute("""
        SELECT sm.id, sm.product_id, sm.name, sm.date
        FROM stock_move sm
        INNER JOIN stock_location loc_from
        ON sm.location_id = loc_from.id
        INNER JOIN stock_location loc_to
        ON sm.location_dest_id = loc_to.id
        WHERE (loc_from.company_id IS NOT NULL
                OR loc_from.usage = 'internal')
            AND (loc_to.company_id IS NULL
                OR loc_from.usage <> 'internal')
            AND sm.state = 'done'
    """)
    for move, product, move_name, move_date in env.cr.fetchall():
        env.cr.execute("""
            SELECT DISTINCT am.id
            FROM account_move_line aml
            INNER JOIN account_move am
            ON aml.move_id = am.id
            WHERE aml.product_id = %s
                AND aml.name = %s
                AND DATE_TRUNC('day', am.date) = to_date(%s, 'YYYY/MM/DD')
        """, (product, move_name, move_date))
        for am in env.cr.fetchall():
            openupgrade.logger.debug("%s" % move_date)
            env.cr.execute("""
                UPDATE account_move
                SET stock_move_id = %s
                WHERE id = %s
            """, (move, am))


def update_stock_move_value_fifo(env):
    """New fields 'value', 'remaining_qty' and 'remaining_value' in
    stock.move need to be properly filled for environments using
    perpetual/automated inventory valuation and to not lose the possibility
    to switch to it after migration in envs with manual valuation.
    """
    # Valuate incoming moves:
    env.cr.execute("""
        SELECT sm.id, pt.id, sm.price_unit, sm.product_uom_qty
        FROM stock_move sm
        INNER JOIN stock_location loc_from
        ON sm.location_id = loc_from.id
        INNER JOIN stock_location loc_to
        ON sm.location_dest_id = loc_to.id
        INNER JOIN product_product pp
        ON sm.product_id = pp.id
        INNER JOIN product_template pt
        ON pp.product_tmpl_id = pt.id
        WHERE (loc_from.company_id IS NULL
                OR loc_from.usage <> 'internal')
            AND (loc_to.company_id IS NOT NULL
                OR loc_from.usage = 'internal')
            AND sm.state = 'done'
    """)
    for move, tmpl_id, price_unit, product_uom_qty in env.cr.fetchall():
        # Update remaining value and remaining qty based on quants that
        # still exist in internal locations.
        env.cr.execute("""
            UPDATE stock_move AS to_update
            SET remaining_value = q1.remaining_value,
                remaining_qty = q1.remaining_qty
            FROM (
                SELECT sum(sq.quantity*sq.cost) as remaining_value,
                    sum(sq.quantity) as remaining_qty
                FROM stock_quant_move_rel sqsm
                INNER JOIN stock_quant sq
                ON sqsm.quant_id = sq.id
                INNER JOIN stock_location sl
                ON sq.location_id = sl.id
                WHERE sqsm.move_id = %s
                    AND (sl.company_id IS NOT NULL
                        OR sl.usage = 'internal')
                ) AS q1
            WHERE to_update.id = %s
        """, (move, move))
        # Update value based on quants that a linked to this move.
        env.cr.execute("""
            UPDATE stock_move AS to_update
            SET value = q1.value
            FROM (
                SELECT sum(sq.quantity*sq.cost) as value
                FROM stock_quant_move_rel sqsm
                INNER JOIN stock_quant sq
                ON sqsm.quant_id = sq.id
                WHERE sqsm.move_id = %s
                ) AS q1
            WHERE to_update.id = %s
        """, (move, move))

    # Valuate outgoing moves:
    env.cr.execute("""
        SELECT sm.id, pt.id, sm.price_unit, sm.product_uom_qty
        FROM stock_move sm
        INNER JOIN stock_location loc_from
        ON sm.location_id = loc_from.id
        INNER JOIN stock_location loc_to
        ON sm.location_dest_id = loc_to.id
        INNER JOIN product_product pp
        ON sm.product_id = pp.id
        INNER JOIN product_template pt
        ON pp.product_tmpl_id = pt.id
        WHERE (loc_from.company_id IS NOT NULL
                OR loc_from.usage = 'internal')
            AND (loc_to.company_id IS NULL
                OR loc_from.usage <> 'internal')
            AND sm.state = 'done'
    """)
    for move, tmpl_id, price_unit, product_uom_qty in env.cr.fetchall():
        # Update value based on quants that a linked to this move.
        env.cr.execute("""
            UPDATE stock_move AS to_update
            SET value = -q1.value
            FROM (
                SELECT sum(sq.quantity*sq.cost) as value
                FROM stock_quant_move_rel sqsm
                INNER JOIN stock_quant sq
                ON sqsm.quant_id = sq.id
                WHERE sqsm.move_id = %s
                ) AS q1
            WHERE to_update.id = %s
        """, (move, move))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # set_stock_move_id_for_account_moves(env) # TODO: not sure if we'll do
    update_stock_move_value_fifo(env)
