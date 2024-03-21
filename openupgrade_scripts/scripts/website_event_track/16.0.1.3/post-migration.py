from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "website_event_track", "16.0.1.3/noupdate_changes.xml"
    )
