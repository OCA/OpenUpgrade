# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql

column_copies = {
    'project_project': [
        ('analytic_account_id', None, None),
    ],
}


def compute_project_task_rating_last_value(env):
    # The computing process for this value is slow if you have many tasks.
    # Thus, we compute rating_last_value using SQL because is faster.
    if not openupgrade.column_exists(
            env.cr, 'project_task', 'rating_last_value'):
        openupgrade.logged_query(
            env.cr, """
            ALTER TABLE project_task
            ADD COLUMN rating_last_value DOUBLE PRECISION""",
        )
        openupgrade.logged_query(
            env.cr, """UPDATE project_task pt
            SET rating_last_value = rr.rating
            FROM rating_rating rr
            WHERE rr.res_model = 'project.task' AND rr.res_id = pt.id
            """
        )


def fill_project_project_inherits_values(env):
    """Do this on pre-migration for avoiding temporary error on null names."""
    # Fields already exists, so we only need to add SQL columns
    openupgrade.logged_query(
        env.cr, """ALTER TABLE project_project
            ADD COLUMN name VARCHAR,
            ADD COLUMN partner_id int4,
            ADD COLUMN company_id int4""")
    openupgrade.logged_query(
        env.cr, sql.SQL(
            """UPDATE project_project pp
            SET name = aaa.name, partner_id = aaa.partner_id,
                company_id = aaa.company_id
            FROM account_analytic_account aaa
            WHERE pp.{} = aaa.id"""
        ).format(
            sql.Identifier('analytic_account_id'),
        )
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_project_project_inherits_values(env)
    openupgrade.copy_columns(env.cr, column_copies)
    compute_project_task_rating_last_value(env)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'project', ['ir_cron_rating_project',
                         'rating_project_request_email_template'], True)
    openupgrade.delete_records_safely_by_xml_id(
        env, ['project.duplicate_field_xmlid'],
    )
