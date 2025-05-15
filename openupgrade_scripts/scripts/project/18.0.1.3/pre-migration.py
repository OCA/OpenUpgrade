from openupgradelib import openupgrade

_field_renames = [
    ("project.project", "project_project", "analytic_account_id", "account_id"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
