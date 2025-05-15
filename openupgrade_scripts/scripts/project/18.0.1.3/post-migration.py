from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "project", "18.0.1.3/noupdate_changes.xml")
