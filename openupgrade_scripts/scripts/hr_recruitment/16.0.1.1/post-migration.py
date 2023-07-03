from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr_recruitment", "16.0.1.1/noupdate_changes.xml")
