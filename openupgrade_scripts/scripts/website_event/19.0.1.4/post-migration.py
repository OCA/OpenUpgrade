from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Map menu_type values removed in 19.0 to the new "other" key."""
    env["website.event.menu"].search(
        [("menu_type", "in", ("location", "track", "track_proposal"))]
    ).menu_type = "other"
