# Copyright 2023 Trần Trường Sơn
# Copyright 2023 Rémy Taymans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_new_fields = [
    (
        "is_closed",  # Field name
        "project.task",  # Model name
        "project_task",  # Table name
        "boolean",  # Odoo Field type (in lower case)
        False,  # [Optional] SQL type (if custom fields)
        "project",  # Module name
        False,  # [Optional] Default value
    ),
    (
        "ancestor_id",  # Field name
        "project.task",  # Model name
        "project_task",  # Table name
        "many2one",  # Odoo Field type (in lower case)
        False,  # [Optional] SQL type (if custom fields)
        "project",  # Module name
        False,  # [Optional] Default value
    ),
    (
        "is_analytic_account_id_changed",  # Field name
        "project.task",  # Model name
        "project_task",  # Table name
        "boolean",  # Odoo Field type (in lower case)
        False,  # [Optional] SQL type (if custom fields)
        "project",  # Module name
        False,  # [Optional] Default value
    ),
    (
        "allow_milestones",  # Field name
        "project.project",  # Model name
        "project_project",  # Table name
        "boolean",  # Odoo Field type (in lower case)
        False,  # [Optional] SQL type (if custom fields)
        "project",  # Module name
        False,  # [Optional] Default value
    ),
]


def _set_task_type_fold_if_is_closed(env):
    """Field `is_closed` on project.task.type is removed. The field
    `fold` can be used instead.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task_type
        SET fold = TRUE
        WHERE is_closed = TRUE;
        """,
    )


def _fill_project_task_is_closed(env):
    """Field `is_closed` on project.task is now a stored field."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task task
        SET is_closed = stage.fold
        FROM project_task_type stage
        WHERE task.stage_id = stage.id;
        """,
    )


def _fill_project_last_update_status_if_null(env):
    """In some cases, the user can go to the DB and reset the
    `last_update_status` field to NULL. In version 16.0 it is necessary
    to reset it to `to_define` because it has a `required` attribute.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project project
        SET last_update_status = 'to_define'
        WHERE last_update_status IS NULL;
        """,
    )


def _compute_project_task_ancestor_id(env):
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


def _compute_project_task_is_analytic_account_id_changed(env):
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


def _fill_project_allow_milestones(env):
    """New field allow_milestones on project.project depends on the
    value of the configuration (based on a group)
    project.group_project_milestone.
    Previously, milestone where visible by default on a project. To keep
    this behaviour with existing project, allow_milestones need to be
    set to True.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project project
        SET allow_milestones = true
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _new_fields)
    _set_task_type_fold_if_is_closed(env)
    _fill_project_task_is_closed(env)
    _fill_project_last_update_status_if_null(env)
    _fill_project_allow_milestones(env)
    _compute_project_task_ancestor_id(env)
    _compute_project_task_is_analytic_account_id_changed(env)

    # Remove SQL view project_task_burndown_chart_report not used anymore in Odoo v16.0
    openupgrade.logged_query(
        env.cr, "DROP VIEW IF EXISTS project_task_burndown_chart_report CASCADE"
    )
