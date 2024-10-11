from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "account.analytic.line",
                "account_analytic_line",
                "ancestor_task_id",
                "parent_task_id",
            )
        ],
    )
