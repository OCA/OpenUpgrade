# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def project_project_allow_recurring_tasks(env):
    """
    Set project_project#allow_recurring_tasks if there's a recurring task in
    project
    """
    env.cr.execute(
        """
        UPDATE project_project
        SET allow_recurring_tasks=True
        FROM
        project_task
        WHERE
        project_task.project_id=project_project.id
        AND
        project_task.recurring_task
        """
    )


def project_task_type_rating(env):
    """
    Rating related fields have been moved from project.project to project.task.type
    Use settings from most recent project
    """
    for task_type in env["project.task.type"].search([("project_ids", "!=", False)]):
        env.cr.execute(
            """
            SELECT
            rating_active, rating_request_deadline,
            rating_status, rating_status_period
            FROM project_project
            WHERE id in %s
            ORDER BY write_date DESC
            LIMIT 1
            """,
            (
                tuple(
                    (
                        task_type.project_ids
                        or task_type.with_context(active_test=False).project_ids
                    ).ids
                ),
            ),
        )
        for vals in env.cr.dictfetchall():
            task_type.write(vals)


def project_task_priority(env):
    """
    Map priorities of "1" (v18 high) to "2" (v19 high), but only if there are no
    existing priorities of "2" or "3", pointing to project_task_add_very_high
    being installed in v18
    """
    env.cr.execute(
        "SELECT EXISTS (SELECT id FROM project_task WHERE priority IN ('2', '3'))"
    )
    if env.cr.fetchone()[0]:
        return
    env.cr.execute(
        """
        UPDATE project_task
        SET
        priority='2'
        WHERE
        priority='1'
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    project_project_allow_recurring_tasks(env)
    project_task_type_rating(env)
    project_task_priority(env)
    openupgrade.load_data(
        env,
        "project",
        "19.0.1.4/noupdate_changes.xml",
    )
    openupgrade.delete_record_translations(
        env.cr,
        "project",
        [
            "mail_template_data_project_task",
            "rating_project_request_email_template",
        ],
        ["body_html"],
    )
