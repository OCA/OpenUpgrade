from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(env.cr, "crm_lead", "description", "description")
    openupgrade.logged_query(
        env.cr,
        """
            ALTER TABLE crm_team_member
            ADD COLUMN IF NOT EXISTS assignment_max INTEGER;
            UPDATE crm_team_member
            SET assignment_max = 30;
        """,
    )
