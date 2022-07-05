from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(env.cr, "crm_lead", "description", "description")
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE crm_team_member
        ADD COLUMN assignment_max INTEGER DEFAULT 30;
        ALTER TABLE crm_team_member ALTER COLUMN assignment_max DROP DEFAULT;
        """,
    )
