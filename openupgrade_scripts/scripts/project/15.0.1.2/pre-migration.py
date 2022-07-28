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
                "TRUE",
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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    fill_project_project_allow_task_dependencies(env)
    fill_project_project_last_update_status(env)
