from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env, "hr_holidays_attendance", "18.0.1.0/noupdate_changes.xml"
    )
