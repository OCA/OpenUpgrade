from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # pre-migration of module base converted name column from utm_campaign
    # into jsonb, hence it suffices to copy the name column into title.
    openupgrade.copy_columns(env.cr, {"utm_campaign": [("name", "title", "jsonb")]})
