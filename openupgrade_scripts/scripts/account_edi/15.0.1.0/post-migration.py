from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "account_edi",
        "15.0.1.0/noupdate_changes.xml",
    )
