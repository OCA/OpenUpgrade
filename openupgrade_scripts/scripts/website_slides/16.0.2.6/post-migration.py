from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_slides", "16.0.2.6/noupdate_changes.xml")
