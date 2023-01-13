from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_user_input
        SET end_datetime = (
            SELECT create_date FROM survey_user_input_line
            WHERE user_input_id = survey_user_input.id
            ORDER BY create_date DESC
            LIMIT 1)
        WHERE state = 'done'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_survey
        SET user_id = create_uid
        """,
    )
