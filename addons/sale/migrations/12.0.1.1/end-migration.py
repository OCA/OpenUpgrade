# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def recompute_sale_order_line_qty_delivered(env):
    sale_lines = env['sale.order.line'].search([])
    sale_lines._compute_qty_delivered()
    # assure same values
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET qty_delivered_method = 'manual',
            qty_delivered_manual = %(qty_d)s
        WHERE qty_delivered != %(qty_d)s OR qty_delivered_method = 'manual'
        RETURNING id""",
        {'qty_d': AsIs(openupgrade.get_legacy_name('qty_delivered'))}
    )
    manual_so_lines = env['sale.order.line'].browse(
        [row[0] for row in env.cr.fetchall()])
    for sol in manual_so_lines:
        sol.qty_delivered = sol.qty_delivered_manual


@openupgrade.migrate()
def migrate(env, version):
    recompute_sale_order_line_qty_delivered(env)
