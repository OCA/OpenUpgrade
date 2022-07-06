from openupgradelib import openupgrade


def _copy_columns(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "mail_activity_type": [
                ("force_next", None, None),
                ("res_model_id", None, None),
            ],
            "mail_message_res_partner_needaction_rel": [("failure_type", None, None)],
        },
    )


def _rename_fields(env):
    openupgrade.rename_fields(
        env,
        [
            (
                "mail.activity.type",
                "mail_activity_type",
                "default_next_type_id",
                "triggered_next_type_id",
            ),
            (
                "mail.activity.type",
                "mail_activity_type",
                "next_type_ids",
                "suggested_next_type_ids",
            ),
            (
                "mail.activity.type",
                "mail_activity_type",
                "default_description",
                "default_note",
            ),
            ("mail.message", "mail_message", "no_auto_thread", "reply_to_force_new"),
            ("mail.notification", "mail_notification", "mail_id", "mail_mail_id"),
            ("mail.mail", "mail_mail", "notification", "is_notification"),
        ],
    )


def _rename_tables(env):
    openupgrade.rename_tables(
        env.cr, [("mail_message_res_partner_needaction_rel", "mail_notification")]
    )


def _delete_channel_follower_records(env):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mail_followers
        WHERE partner_id IS NULL;
        """,
    )


def _delete_mail_channel_partner_duplicate_records(env):
    # Cleanup potential duplicates to comply with
    # the new constraint mail_channel_partner_partner_unique
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mail_channel_partner mcp1
        USING mail_channel_partner mcp2
        WHERE mcp1.id < mcp2.id
            AND mcp1.partner_id = mcp2.partner_id
            AND mcp1.channel_id = mcp2.channel_id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _delete_mail_channel_partner_duplicate_records(env)
    _copy_columns(env)
    _rename_tables(env)
    _rename_fields(env)
    _delete_channel_follower_records(env)
