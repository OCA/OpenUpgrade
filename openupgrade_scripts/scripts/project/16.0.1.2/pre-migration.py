from odoo.tools.sql import column_exists, create_column


def _move_task_stage_is_closed_to_fold(cr):
    cr.execute(
        """
        UPDATE project_task_type
        SET fold = TRUE
        WHERE is_closed = TRUE
    """
    )


def _update_project_last_update_status(cr):
    cr.execute(
        """
        UPDATE project_project project
        SET last_update_status = 'to_define'
        WHERE last_update_status IS NULL
    """
    )


def _set_task_is_analytic_account_id_changed_value(cr):
    if not column_exists(cr, 'project_task', 'is_analytic_account_id_changed'):
        create_column(cr, 'project_task', 'is_analytic_account_id_changed', 'boolean')

    cr.execute(
        """
        UPDATE project_task task
        SET is_analytic_account_id_changed = CASE
            WHEN task.analytic_account_id = project.analytic_account_id THEN FALSE
            ELSE TRUE
            END
        FROM project_project as project
        WHERE task.project_id = project.id
    """
    )


def _set_task_is_closed_value(cr):
    if not column_exists(cr, "project_task", "is_closed"):
        create_column(cr, "project_task", "is_closed", "boolean")

    cr.execute(
        """
        UPDATE project_task task
        SET is_closed = CASE
            WHEN stage.fold = TRUE THEN TRUE
            ELSE FALSE
            END
        FROM project_task_type stage
        WHERE task.stage_id = stage.id
    """
    )


def _set_task_is_blocked_value(cr):
    if not column_exists(cr, "project_task", "is_blocked"):
        create_column(cr, "project_task", "is_blocked", "boolean")

    cr.execute(
        """
        WITH cte AS (
            SELECT
                t.id,
                CASE
                    WHEN COUNT(t.id) > 0 THEN TRUE
                    ELSE FALSE
                END AS is_blocked
            FROM
                project_task t
            LEFT JOIN
                task_dependencies_rel d ON d.task_id = t.id
            LEFT JOIN
                project_task d_task ON d_task.id = d.depends_on_id
            WHERE d_task.is_closed = FALSE
            GROUP BY t.id
        )

        UPDATE project_task task
        SET is_blocked = cte.is_blocked
        FROM cte
        WHERE task.id = cte.id
    """
    )


def migrate(cr, version):
    _move_task_stage_is_closed_to_fold(cr)
    _update_project_last_update_status(cr)
    _set_task_is_analytic_account_id_changed_value(cr)
    _set_task_is_closed_value(cr)
    _set_task_is_blocked_value(cr)
