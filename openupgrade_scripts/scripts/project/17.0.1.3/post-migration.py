# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "project.ir_cron_recurring_tasks",
    "project.mt_project_task_blocked",
    "project.mt_project_task_dependency_change",
    "project.mt_project_task_ready",
    "project.mt_task_blocked",
    "project.mt_task_dependency_change",
    "project.mt_task_progress",
    "project.mt_task_ready",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "project", "17.0.1.3/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task
        SET display_in_project = TRUE
        WHERE display_project_id IS NOT NULL;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task
        SET state = CASE
            WHEN kanban_state = 'done' THEN '1_done'
            WHEN kanban_state = 'blocked' THEN '04_waiting_normal'
            ELSE '01_in_progress'
        END
        WHERE kanban_state IN ('done', 'blocked', 'normal');
        """,
    )
