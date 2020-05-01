# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate_project_sale_order(env):
    openupgrade.logged_query(
        env.cr, """
            UPDATE project_project p
            SET sale_order_id = sol.order_id
            FROM sale_order_line sol
            WHERE sol.id = p.sale_line_id
            AND p.sale_order_id != sol.order_id
        """)


@openupgrade.migrate()
def migrate(env, version):
    migrate_project_sale_order(env)
