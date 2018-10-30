# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def migrate_sale_line_tasks(env):
    openupgrade.logged_query(
        env.cr, """
            UPDATE sale_order_line sol
            SET task_id = po.task_id
            FROM procurement_order po
            WHERE sol.id = po.sale_line_id
        """)


def migrate_project_sale_line(env):
    service_column = openupgrade.get_legacy_name('service_type')
    openupgrade.logged_query(
        env.cr, """
            UPDATE project_project pj
            SET sale_line_id = sub.sol_id
            FROM (
                SELECT * FROM (
                    SELECT pj.id AS project_id,
                        sol.id AS sol_id,
                        row_number() over (
                            partition BY pj.id ORDER BY pj.id
                        ) AS rnum
                    FROM project_project pj,
                        sale_order_line sol,
                        product_product pd,
                        sale_order so,
                        product_template pt
                    WHERE sol.product_id = pd.id
                        AND sol.order_id = so.id
                        AND so.analytic_account_id = pj.id
                        AND pt.id = pd.product_tmpl_id
                        AND so.state in ('sale', 'done')
                        AND pt.%s in ('task', 'timesheet')
                        AND pj.create_date > so.create_date
                ) t
                WHERE t.rnum = 1
            ) AS sub
            WHERE sub.project_id = pj.id
        """, (AsIs(service_column),))


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('service_type'), 'service_type',
        [('task', 'timesheet')], table='product_template',
    )
    # Update invoice_policy
    env['product.template'].search([
        ('type', '=', 'service'),
    ])._compute_service_policy()
    migrate_sale_line_tasks(env)
    migrate_project_sale_line(env)
