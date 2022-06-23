from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
            ALTER TABLE project_project
            ADD COLUMN IF NOT EXISTS last_update_status CHARACTER VARYING;
            UPDATE project_project
            SET last_update_status = 'on_track';
        """,
    )
