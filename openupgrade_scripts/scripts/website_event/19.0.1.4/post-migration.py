from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # menu_type 'location'/'track'/'track_proposal' dropped in 19.0 → 'other'
    env["website.event.menu"].search(
        [("menu_type", "in", ("location", "track", "track_proposal"))]
    ).menu_type = "other"
    openupgrade.load_data(env, "website_event", "19.0.1.4/noupdate_changes.xml")
