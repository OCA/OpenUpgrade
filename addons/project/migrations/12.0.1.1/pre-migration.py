# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    compute_project_task_rating_last_value(env)
