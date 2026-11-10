# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def discuss_channel_member_channel_role(env):
    """
    Set discuss.channel.member#channel_role to 'owner' for backend users who created a
    channel
    """
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE
            discuss_channel_member
        SET
            channel_role='owner'
        FROM
            res_users,
            discuss_channel
        WHERE
            channel_type IN ('group', 'channel')
        AND
            discuss_channel_member.channel_id=discuss_channel.id
        AND
            res_users.partner_id=discuss_channel_member.partner_id
        AND
            res_users.id=discuss_channel.create_uid
        AND
            NOT EXISTS (
                SELECT uid FROM res_groups_users_rel
                WHERE uid=res_users.id AND gid={env.ref("base.group_public").id}
            )
        """,
    )


def mail_activity_type_suggested_next_type_id(env):
    """
    Fill mail.activity.type#suggested_next_type_id from
    mail.activity.type#suggested_next_type_ids
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            mail_activity_type
        SET
            suggested_next_type_id=mail_activity_rel.recommended_id
        FROM
            mail_activity_rel
        WHERE
            mail_activity_rel.activity_id=mail_activity_type.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "mail",
        "20.0.1.19/noupdate_changes.xml",
        xml_transformation_filename="20.0.1.19/noupdate_changes-transformation.xml",
    )
    discuss_channel_member_channel_role(env)
    mail_activity_type_suggested_next_type_id(env)
