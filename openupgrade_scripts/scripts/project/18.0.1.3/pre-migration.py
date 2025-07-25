from openupgradelib import openupgrade

_field_renames = [
    ("project.project", "project_project", "analytic_account_id", "account_id"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    rule = env.ref(
        "project_todo.task_visibility_rule_project_user", raise_if_not_found=False
    )
    if rule:
        openupgrade.rename_xmlids(
            env.cr,
            [
                (
                    "project_todo.task_visibility_rule_project_user",
                    "project.task_visibility_rule_project_user",
                )
            ],
        )
