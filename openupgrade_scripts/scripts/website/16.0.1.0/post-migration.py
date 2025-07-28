from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website", "16.0.1.0/noupdate_changes.xml")
    # Website editors that come from v15, where there was no sanitization, would expect
    # the same on the new version, or worst: they introduce some content like iframe,
    # and re-editing that content in 16 leads to lose it when saving it. Thus, let's
    # add all of them to the override sanitization group for keeping the same behavior.
    users = env.ref("website.group_website_restricted_editor").users
    users.groups_id = [(4, env.ref("base.group_sanitize_override").id)]
