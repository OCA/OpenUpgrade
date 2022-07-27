from openupgradelib import openupgrade


def _map_activity_type_chaining_type_field(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("force_next"),
        "chaining_type",
        [("true", "trigger"), ("false", "suggest")],
        table="mail_activity_type",
    )


def _map_activity_type_res_model_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_activity_type
        SET res_model = ir_model.model
        FROM ir_model
        WHERE mail_activity_type.%s = ir_model.id
        """
        % openupgrade.get_legacy_name("res_model_id"),
    )


def _map_mail_notification_failure_type(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("failure_type"),
        "failure_type",
        [
            ("SMTP", "mail_smtp"),
            ("BOUNCE", "mail_email_invalid"),
            ("RECIPIENT", "mail_email_invalid"),
            ("UNKNOWN", "unknown"),
        ],
        table="mail_notification",
    )


def finish_migration_to_mail_group(env):
    env.cr.execute(
        """
        SELECT 1 FROM ir_module_module
        WHERE name = 'mail_group' AND state = 'to install'""",
    )
    will_have_mail_group = env.cr.rowcount
    if not will_have_mail_group:
        return
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_attachment ia
        USING mail_channel mc
        WHERE ia.res_model = 'mail.channel' AND ia.res_id = mc.id
            AND mc.email_send AND ia.res_field = 'image_128'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mail_channel
        WHERE email_send""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "mail", "15.0.1.5/noupdate_changes.xml")
    _map_activity_type_chaining_type_field(env)
    _map_activity_type_res_model_field(env)
    _map_mail_notification_failure_type(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "mail.mail_moderation_rule_user",
            "mail.ir_cron_mail_notify_channel_moderators",
        ],
    )
    finish_migration_to_mail_group(env)
