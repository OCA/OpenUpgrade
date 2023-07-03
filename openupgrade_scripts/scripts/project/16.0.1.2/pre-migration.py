from openupgradelib import openupgrade


def _create_column_for_avoiding_automatic_computing(env):
    """
    Create some new columns in the database and set values for them
    to avoid computing by ORM
    """
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_project
          ADD COLUMN IF NOT EXISTS allow_milestones boolean;
        """,
    )
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
        ALTER TABLE project_task
          ADD COLUMN IF NOT EXISTS is_closed boolean;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE project_task
          ADD COLUMN IF NOT EXISTS ancestor_id integer;
        """,
    )


def _fill_proejct_allow_milestones(env):
    # Set True if had milestone
    openupgrade.logged_query(
        env.cr,
        """
        WITH cte as (
            SELECT project_id, count(*) as milestone_count
              FROM project_milestone
             GROUP BY project_id
        )

        UPDATE project_project project
           SET allow_milestones = CASE
               WHEN cte.milestone_count > 0 THEN TRUE
               ELSE FALSE
               END
          FROM cte
         WHERE project.id = cte.project_id;
        """,
    )


def _fill_project_last_update_status_if_null(env):
    """
    In some cases, the user can go to the DB and reset the `last_update_status`
    field to NULL. In version 16.0 it is necessary to reset it to `to_define`
    because it has a `required` attribute.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project project
           SET last_update_status = 'to_define'
         WHERE last_update_status IS NULL;
        """,
    )


def _set_task_stage_type_to_fold_if_is_closed(env):
    """
    In version 16.0, task stages with type `is_closed` will be removed.
    just use the `fold` style instead. Therefore, it is necessary to define
    the phase types as `is_closed` and return them to `fold`
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
           SET fold = TRUE
         WHERE is_closed = TRUE;
        """,
    )


def _fill_project_task_is_analytic_account_id_changed(env):
    """
    `is_analytic_account_id_changed` is a new field at version 16.0.
    It has a value of False if you have the same admin account as the project,
    otherwise it will have a value of True
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task task
           SET is_analytic_account_id_changed = CASE
                WHEN project_id IS NOT NULL
                 AND task.project_id = project.id
                 AND task.analytic_account_id != project.analytic_account_id
                THEN TRUE
                ELSE FALSE
                 END
          FROM project_project as project;
        """,
    )


def _fill_project_task_is_closed(env):
    # `is_closed` field will be store at version 16.0
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


def _fil_project_task_ancestor_id(env):
    """
    New column at version 16.0. valid as the ancestor of the current task
    """
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
    _fill_project_task_is_analytic_account_id_changed(env)
    _set_task_stage_type_to_fold_if_is_closed(env)
    _fill_project_task_is_analytic_account_id_changed(env)
    _fill_project_task_is_closed(env)
    _fil_project_task_ancestor_id(env)
