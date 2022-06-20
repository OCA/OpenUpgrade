from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_survey
        SET active = CASE WHEN state IN ('draft','open') THEN true ELSE false END
        WHERE active = true
        """,
    )
