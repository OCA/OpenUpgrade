from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE im_livechat_channel_rule
        SET chatbot_enabled_condition = 'always'
        WHERE chatbot_enabled_condition IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE im_livechat_channel_rule
        SET chatbot_enabled_condition = 'only_if_no_operator'
        WHERE chatbot_only_if_no_operator = TRUE
        """,
    )
