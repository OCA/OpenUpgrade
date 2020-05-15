# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Pedro M. Baeza
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
    service_column = openupgrade.get_legacy_name('track_service')
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
                        AND so.analytic_account_id = pj.analytic_account_id
                        AND pt.id = pd.product_tmpl_id
                        AND so.state in ('sale', 'done')
                        AND pt.%s in ('task', 'timesheet')
                        AND pj.create_date > so.create_date
                ) t
                WHERE t.rnum = 1
            ) AS sub
            WHERE sub.project_id = pj.id
        """, (AsIs(service_column),))


def map_track_service(env):
    """"Map values for old `track_service` field (copied in sale pre-migration)
    according this mapping:

    track_service           service_tracking
    -------------           ----------------
    'manual'		         'no'
    'task'                  if not project_id: 'task_new_project'
                            if project_id: 'task_global_project'
    'timesheet'             'project_only'

    Project field depends on company, so this is applicable as soon as one
    company has any project set.
    """
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('track_service'),
        'service_tracking', [
            ('manual', 'no'),
            ('timesheet', 'project_only'),
        ], table='product_template',
    )
    # Need to be done through subquery as unique option for proper joining
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template pt
        SET service_tracking = 'task_new_project'
        FROM (
            SELECT pt.id FROM
            product_template pt
            JOIN ir_model_fields imf ON imf.name = 'project_id'
                AND imf.model = 'product.template'
            LEFT JOIN ir_property ip ON ip.fields_id = imf.id
                AND ip.res_id = 'product.template,' || pt.id::text
            WHERE pt.%s = 'task'
                AND ip.value_reference IS NULL
        ) sub
        WHERE sub.id = pt.id""",
        (AsIs(openupgrade.get_legacy_name('track_service')), ),
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_template pt
        SET service_tracking = 'task_global_project'
        FROM (
            SELECT pt.id FROM
            product_template pt
            JOIN ir_model_fields imf ON imf.name = 'project_id'
                AND imf.model = 'product.template'
            LEFT JOIN ir_property ip ON ip.fields_id = imf.id
                AND ip.res_id = 'product.template,' || pt.id::text
            WHERE pt.%s = 'task'
                AND ip.value_reference IS NOT NULL
        ) sub
        WHERE sub.id = pt.id""",
        (AsIs(openupgrade.get_legacy_name('track_service')), ),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('track_service'), 'service_type',
        [('task', 'timesheet')], table='product_template',
    )
    map_track_service(env)
    # Update invoice_policy
    env['product.template'].search([
        ('type', '=', 'service'),
    ])._compute_service_policy()
    migrate_sale_line_tasks(env)
    migrate_project_sale_line(env)
