from openupgradelib import openupgrade


def _create_column_for_avoiding_automatic_computing(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task
        ADD COLUMN IF NOT EXISTS is_analytic_account_id_changed boolean;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task ADD COLUMN IF NOT EXISTS is_closed boolean;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task ADD COLUMN IF NOT EXISTS is_blocked boolean;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task ADD COLUMN IF NOT EXISTS ancestor_id integer;
        """,
    )


def _fill_project_last_update_status_if_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project project
        SET last_update_status = 'to_define'
        WHERE last_update_status IS NULL;
        """,
    )


def _set_task_stage_type_to_fold_if_is_closed(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
        SET fold = TRUE
        WHERE is_closed = TRUE;
        """,
    )


def _fill_project_task_is_analytic_account_id_changed(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task task
        SET is_analytic_account_id_changed = CASE
            WHEN task.analytic_account_id = project.analytic_account_id THEN FALSE
            ELSE TRUE
            END
        FROM project_project as project
        WHERE task.project_id = project.id;
        """,
    )


def _fill_project_task_is_closed(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task task
        SET is_closed = CASE
            WHEN stage.fold = TRUE THEN TRUE
            ELSE FALSE
            END
        FROM project_task_type stage
        WHERE task.stage_id = stage.id;
        """,
    )


def _fill_project_task_is_blocked(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task
        SET is_blocked = TRUE
        WHERE id IN (
            SELECT task_id
            FROM task_dependencies_rel
            WHERE depends_on_id IN (SELECT id FROM project_task WHERE is_closed = FALSE)
        );

        UPDATE project_task
        SET is_blocked = FALSE
        WHERE id NOT IN (
            SELECT task_id
            FROM task_dependencies_rel
            WHERE depends_on_id IN (SELECT id FROM project_task WHERE is_closed = FALSE)
        );
        """,
    )


def _fil_project_task_ancestor_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH RECURSIVE task_ancestors AS (
            SELECT id, parent_id, id AS ancestor_id
            FROM project_task
            WHERE parent_id IS NULL

            UNION ALL

            SELECT pt.id, pt.parent_id, ta.ancestor_id
            FROM project_task pt
            INNER JOIN task_ancestors ta ON pt.parent_id = ta.id
        )

        UPDATE project_task pt
        SET ancestor_id = ta.ancestor_id
        FROM task_ancestors ta
        WHERE pt.id = ta.id;

        UPDATE project_task pt
        SET ancestor_id = NULL
        WHERE id = ancestor_id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_column_for_avoiding_automatic_computing(env)
    _fill_project_last_update_status_if_null(env)
    _set_task_stage_type_to_fold_if_is_closed(env)
    _fill_project_task_is_analytic_account_id_changed(env)
    _fill_project_task_is_closed(env)
    _fill_project_task_is_blocked(env)
    _fil_project_task_ancestor_id(env)
