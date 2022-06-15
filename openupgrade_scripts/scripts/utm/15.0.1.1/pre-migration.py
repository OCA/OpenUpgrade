from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(
        env.cr,
        {
            "utm_campaign": [
                ("is_website", "is_auto_campaign"),
            ],
        },
    )
