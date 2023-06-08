# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_fields_renames = [
    (
        "mail.channel",
        "mail_channel",
        "channel_last_seen_partner_ids",
        "channel_member_ids",
    )
]
_models_renames = [("mail.channel.partner", "mail.channel.member")]
_tables_renames = [("mail_channel_partner", "mail_channel_member")]
_columns_renames = {
    "mail_message": [("add_sign", "email_add_signature")],
}
_xmlids_renames = [
    (
        "mail.channel_partner_general_channel_for_admin",
        "mail.channel_member_general_channel_for_admin",
    ),
    (
        "mail.ir_rule_mail_channel_partner_group_system",
        "mail.ir_rule_mail_channel_member_group_system",
    ),
    (
        "mail.ir_rule_mail_channel_partner_group_user",
        "mail.ir_rule_mail_channel_member_group_user",
    ),
]
_columns_copies = {
    "mail_channel_rtc_session": [
        ("channel_partner_id", "channel_member_id", "integer")
    ],
}


def delete_obsolete_constraints(env):
    openupgrade.delete_sql_constraint_safely(
        env, "mail", "mail_channel_partner", "partner_or_guest_exists"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "mail", "mail_channel_rtc_session", "channel_partner_unique"
    )


def ir_act_server_rename_state_email(env):
    """
    ir.actions.server state selection key 'email' is now 'mail_post'.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_act_server
        SET state='mail_post'
        WHERE state='email';
        """,
    )


def mail_channel_channel_type_required(env):
    """
    channel_type is now required on mail.channel.
    Set default value 'channel' if no value was set.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_channel
        SET channel_type='channel'
        WHERE channel_type IS NULL;
        """,
    )


def scheduled_date_set_empty_strings_to_null(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_mail
        SET scheduled_date = NULL
        WHERE scheduled_date = '';
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    delete_obsolete_constraints(env)
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    openupgrade.rename_columns(env.cr, _columns_renames)
    openupgrade.copy_columns(env.cr, _columns_copies)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    ir_act_server_rename_state_email(env)
    mail_channel_channel_type_required(env)
    scheduled_date_set_empty_strings_to_null(env)
