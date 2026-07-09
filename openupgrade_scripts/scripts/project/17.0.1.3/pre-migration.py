# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _rename_fields(env):
    openupgrade.rename_fields(
        env,
        [
            ("project.task", "project_task", "planned_hours", "allocated_hours"),
            (
                "project.task.type",
                "project_task_type",
                "auto_validation_kanban_state",
                "auto_validation_state",
            ),
        ],
    )


def _convert_project_task_state(env):
    """Handle kanban_state, is_closed, etc to state conversion."""
    openupgrade.add_fields(
        env, [("state", "project.task", "project_task", "selection", False, "project")]
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task
        SET state = CASE
            WHEN kanban_state = 'done' THEN CASE
                WHEN is_closed THEN '1_done'
                ELSE '03_approved'
            END
            WHEN kanban_state = 'blocked' THEN CASE
                WHEN is_closed THEN '1_canceled'
                ELSE '02_changes_requested'
            END
            ELSE '01_in_progress'
        END
        WHERE kanban_state IN ('done', 'blocked', 'normal');
        """,
    )
    # Secnd pass for setting '04_waiting_normal' on tasks with "Blocked By" entries
    # that qualify
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_task pt
        SET state = '04_waiting_normal'
        FROM task_dependencies_rel rel
        JOIN project_task dep ON dep.id = rel.depends_on_id
        WHERE rel.task_id = pt.id AND dep.state NOT IN ('1_done', '1_canceled')
        """,
    )


def _set_default_analytic_plan_id(env):
    """
    default analytic_plan_id from res.config.settings has been moved from res.company
    related to ir.config_parameter.
    Since we already set this same plan in analytic pre-migration,
    we reuse it for project
    """
    plan_id = env["ir.config_parameter"].get_param("analytic.project_plan", False)
    if plan_id:
        env["ir.config_parameter"].set_param(
            "analytic.analytic_plan_projects", str(plan_id)
        )


def _delete_project_list_views(env):
    """OCA module project_list got its functionality implemented in core
    odoo. Its ir.actions.act_window.view records (reassigned to 'project'
    module by merged_modules in base pre-migration) collide with v17 core's
    new records on constraint act_window_view_unique_mode_per_action.
    """
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "project.open_view_project_all_group_stage_kanban",
            "project.open_view_project_all_group_stage_tree",
            "project.open_view_project_all_kanban",
            "project.open_view_project_all_tree",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    _rename_fields(env)
    _convert_project_task_state(env)
    _set_default_analytic_plan_id(env)
    _delete_project_list_views(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "project",
        [
            "project_project_stage_0",
            "project_project_stage_1",
            "project_project_stage_2",
            "project_project_stage_3",
        ],
        True,
    )
