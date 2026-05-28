from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_attendance", "19.0.2.0/noupdate_changes.xml")
