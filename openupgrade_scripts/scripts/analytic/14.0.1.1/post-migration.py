from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "analytic", "14.0.1.1/noupdate_changes.xml")
