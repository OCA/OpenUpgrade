from openupgradelib import openupgrade

_column_renames = {
    "project_task": [
        ("user_id", None),
    ],
}


def fill_project_project_allow_task_dependencies(env):
    openupgrade.add_fields(
        env,
        [
            (
                "allow_task_dependencies",
                "project.project",
                "project_project",
                "boolean",
                "bool",
                "project",
                True,
            ),
        ],
    )


def fill_project_project_last_update_status(env):
    openupgrade.add_fields(
        env,
        [
            (
                "last_update_status",
                "project.project",
                "project_project",
                "selection",
                "varchar",
                "project",
                "on_track",
            ),
        ],
    )


def adapt_project_task_dependency(env):
    # check if project_task_dependency was installed
    if not openupgrade.table_exists(env.cr, "project_task_dependency_task_rel"):
        return
    openupgrade.rename_tables(
        env.cr, [("project_task_dependency_task_rel", "task_dependencies_rel")]
    )
    openupgrade.rename_fields(
        env,
        [
            ("project.task", "project_task", "dependency_task_ids", "depend_on_ids"),
            ("project.task", "project_task", "depending_task_ids", "dependent_ids"),
        ],
    )
    openupgrade.rename_columns(
        env.cr, {"task_dependencies_rel": [("dependency_task_id", "depends_on_id")]}
    )


def rename_project_milestone_target_date(env):
    """If project_milestone is installed then rename column target_date
    to deadline.
    """
    if openupgrade.column_exists(env.cr, "project_milestone", "target_date"):
        openupgrade.rename_columns(
            env.cr,
            {"project_milestone": [("target_date", "deadline")]},
        )


def migrate_project_status(env):
    """Migrate project_status module if installed to
    project.project.stages.
    """
    if openupgrade.table_exists(env.cr, "project_status"):
        openupgrade.rename_models(env.cr, [("project.status", "project.project.stage")])
        openupgrade.rename_tables(env.cr, [("project_status", "project_project_stage")])
        openupgrade.rename_fields(
            env,
            [
                (
                    "project.project.stage",
                    "project_project_stage",
                    "status_sequence",
                    "sequence",
                ),
                (
                    "project.project",
                    "project_project",
                    "project_status",
                    "stage_id",
                ),
            ],
        )
        openupgrade.rename_columns(
            env.cr,
            {
                "project_project_stage": [
                    ("company_id", None),
                    ("description", None),
                    ("is_closed", None),
                ],
            },
        )
        # Delete project_status views
        xmlids_views = [
            "project.view_project",
            "project.edit_project",
            "project.project_project_view_form_simplified",
            "project.project_view_kanban",
            "project.view_project_project_filter",
        ]
        openupgrade.delete_records_safely_by_xml_id(
            env, xmlids_views, delete_childs=True
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    adapt_project_task_dependency(env)
    fill_project_project_allow_task_dependencies(env)
    fill_project_project_last_update_status(env)
    rename_project_milestone_target_date(env)
    migrate_project_status(env)
