# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_to_refund_so(env):
    cr = env.cr
    where_clause = "WHERE origin_returned_move_id IS NOT NULL"
    # If there's a migration from v8, use the field to say if return is
    # refundable or not
    column_name = 'openupgrade_legacy_9_0_invoice_state'
    if openupgrade.column_exists(cr, 'stock_move', column_name):
        where_clause += " AND %s != 'none'" % column_name
    query = "SELECT id FROM stock_move %s" % where_clause
    cr.execute(query)
    move_ids = [x[0] for x in cr.fetchall()]
    if not move_ids:
        return
    openupgrade.logged_query(
        cr, "UPDATE stock_move SET to_refund_so=True WHERE id IN %s",
        (tuple(move_ids), ),
    )
    # Recompute delivered quantities
    moves = env['stock.move'].browse(move_ids)
    sale_order_lines = moves.mapped('procurement_id.sale_line_id')
    for line in sale_order_lines:
        line.qty_delivered = line._get_delivered_qty()


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_to_refund_so(env)
