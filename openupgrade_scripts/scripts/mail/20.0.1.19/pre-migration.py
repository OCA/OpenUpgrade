# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_renamed_xmlids = [
    (
        "mail.action_view_mail_tracking_value",
        "mail_tracking.action_view_mail_tracking_value",
    ),
    ("mail.menu_mail_tracking_value", "mail_tracking.menu_mail_tracking_value"),
]

_renamed_tables = [
    ("mail_message_res_partner_starred_rel", "mail_message_res_partner_bookmarked_rel"),
]

_added_columns = [
    ("mail.activity", "phone", "char"),
    ("mail.activity", "role_id", "many2one"),
    ("mail.activity", "technical_usage", "selection", "none"),
    ("mail.activity.plan.template", "role_id", "many2one"),
]


def admin_channel_member_xmlid(env):
    """
    Create an xmlid for admin's channel member in the admin channel
    """
    env.cr.execute(
        """
        SELECT id
        FROM discuss_channel_member
        WHERE
        partner_id = (
            SELECT res_id FROM ir_model_data
            WHERE module='base' and name='partner_admin'
        )
        AND channel_id = (
            SELECT res_id FROM ir_model_data
            WHERE module='mail' and name='channel_admin'
        )
        AND NOT EXISTS (
            SELECT id FROM ir_model_data
            WHERE
            module='mail'
            AND name='channel_member_channel_admin_partner_admin'
        )
        """
    )
    for (_id,) in env.cr.fetchall():
        openupgrade.add_xmlid(
            env.cr,
            "mail",
            "channel_member_channel_admin_partner_admin",
            "discuss.channel.member",
            _id,
        )


def mail_message_message_type_tracking(env):
    """
    Set message_type=tracking for mail.message records with mail.tracking.value records
    Install mail_tracking if the query hit any records
    """
    count = openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            mail_message
        SET
            message_type='tracking'
        FROM (
            SELECT DISTINCT mail_message_id FROM mail_tracking_value
        ) mail_message_value_distinct
        WHERE
            mail_message.id=mail_message_value_distinct.mail_message_id
        """,
    )
    if count:
        env["ir.module.module"].search(
            [("name", "=", "mail_tracking")]
        ).button_install()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
    openupgrade.rename_tables(env.cr, _renamed_tables)
    openupgrade.add_columns(env, _added_columns)
    admin_channel_member_xmlid(env)
    mail_message_message_type_tracking(env)
