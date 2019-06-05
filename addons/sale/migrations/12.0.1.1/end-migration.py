# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def recompute_sale_order_line_qty_delivered(env):
    """Detect lines with a non coincident computed qty_delivered for assigning
    the previous value manually.
    """
    sale_lines = env['sale.order.line'].search([])
    for sol in sale_lines:
        # Create an identical virtual record for not affecting dependent fields
        # on original record, and compute expected qty_delivered in it
        sol2 = sol.new(sol.read()[0])
        sol2._compute_qty_delivered()
        if sol2.qty_delivered != sol.qty_delivered:
            # Save changes in SQL for avoiding recomputations
            env.cr.execute(
                """UPDATE sale_order_line
                SET qty_delivered_method = 'manual',
                    qty_delivered_manual = %s
                WHERE id = %s""",
                (sol2.qty_delivered, sol.id, ),
            )
    openupgrade.logged_query(
        env.cr, """
            UPDATE sale_order_line sol
            SET qty_delivered_manual = %(qty_d)s
            WHERE qty_delivered_method = 'manual'
                AND qty_delivered_manual != %(qty_d)s""",
        {'qty_d': AsIs(openupgrade.get_legacy_name('qty_delivered')), }
    )


@openupgrade.migrate()
def migrate(env, version):
    recompute_sale_order_line_qty_delivered(env)
