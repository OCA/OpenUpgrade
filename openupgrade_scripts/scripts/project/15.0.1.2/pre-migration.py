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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    adapt_project_task_dependency(env)
    fill_project_project_allow_task_dependencies(env)
    fill_project_project_last_update_status(env)
