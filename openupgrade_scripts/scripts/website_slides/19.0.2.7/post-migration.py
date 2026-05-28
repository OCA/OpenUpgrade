from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_slides", "19.0.2.7/noupdate_changes_work.xml")
