from openupgradelib import openupgrade

from odoo.tools import sql


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
    openupgrade.delete_sql_constraint_safely(
        env,
        "mail",
        "mail_message_res_partner_needaction_rel",
        "notification_partner_required",
    )
    # we delete sql constraint before table rename
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


def delete_obsolete_constraints(env):
    _contraints = [
        ("mail", "mail_followers", "mail_followers_res_channel_res_model_id_uniq"),
        ("mail", "mail_followers", "partner_xor_channel"),
        ("mail", "mail_moderation", "channel_email_uniq"),
    ]
    for module, table, name in _contraints:
        openupgrade.delete_sql_constraint_safely(env, module, table, name)
    openupgrade.remove_tables_fks(
        env.cr,
        [
            "mail_moderation",
            "mail_channel_moderator_rel",
            "mail_message_mail_channel_rel",
        ],
    )


def migration_to_mail_group(env):
    env.cr.execute("SELECT 1 FROM mail_moderation LIMIT 1")
    has_moderation = env.cr.rowcount
    env.cr.execute("SELECT 1 FROM mail_channel WHERE email_send LIMIT 1")
    has_old_mail_groups = env.cr.rowcount
    env.cr.execute(
        """
        SELECT 1 FROM ir_module_module
        WHERE name = 'portal' AND state in ('installed', 'to upgrade', 'to install')""",
    )
    has_portal = env.cr.rowcount
    if not (has_moderation or has_old_mail_groups) or not has_portal:
        return
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state='to install'
        WHERE name = 'mail_group' AND state='uninstalled'""",
    )
    openupgrade.rename_models(
        env.cr,
        [
            ("mail.moderation", "mail.group.moderation"),
        ],
    )
    openupgrade.rename_tables(
        env.cr,
        [
            ("mail_moderation", "mail_group_moderation"),
            ("mail_channel_moderator_rel", "mail_group_moderator_rel"),
        ],
    )
    openupgrade.rename_columns(
        env.cr,
        {
            "mail_group_moderator_rel": [
                ("mail_channel_id", "mail_group_id"),
            ]
        },
    )
    # fill mail_group table
    sql.create_model_table(
        env.cr,
        "mail_group",
        columns=[
            ("name", "varchar", ""),
            ("active", "bool", ""),
            ("description", "text", ""),
            ("moderation", "bool", ""),
            ("access_mode", "varchar", ""),
            ("access_group_id", "integer", ""),
            ("moderation_notify", "bool", ""),
            ("moderation_notify_msg", "text", ""),
            ("moderation_guidelines", "bool", ""),
            ("moderation_guidelines_msg", "text", ""),
            ("create_uid", "integer", ""),
            ("write_uid", "integer", ""),
            ("create_date", "timestamp", ""),
            ("write_date", "timestamp", ""),
            ("old_channel_id", "integer", ""),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mail_group (name, active, description, moderation,
            access_group_id, access_mode, moderation_notify, moderation_notify_msg,
            moderation_guidelines, moderation_guidelines_msg,
            create_uid, write_uid, create_date, write_date, old_channel_id)
        SELECT mc.name, mc.active, mc.description, mc.moderation, mc.group_public_id,
            CASE WHEN mc.public = 'private' THEN 'members' ELSE mc.public END,
            mc.moderation_notify, mc.moderation_notify_msg, mc.moderation_guidelines,
            mc.moderation_guidelines_msg, mc.create_uid, mc.write_uid, mc.create_date,
            mc.write_date, mc.id
        FROM mail_channel mc
        WHERE mc.email_send""",
    )
    # add image_128 attachments
    env.cr.execute(
        """
        SELECT ia.*, mg.id AS mail_group_id
        FROM ir_attachment ia
        JOIN mail_channel mc ON (ia.res_model = 'mail.channel' AND ia.res_id = mc.id)
        JOIN mail_group mg ON mg.old_channel_id = mc.id
        WHERE ia.res_field = 'image_128'
        """,
    )
    columns = [
        x.name for x in env.cr._obj.description if x.name not in ("id", "mail_group_id")
    ]
    attachments = env.cr.dictfetchall()
    values = []
    for attachment in attachments:
        attachment["res_model"] = "mail.group"
        attachment["res_id"] = attachment["mail_group_id"]
        vals = ["'%s'" % attachment[x] for x in columns]
        vals = [x if x != "'None'" else "NULL" for x in vals]
        values += ["(" + ", ".join(vals) + ")"]
    if values:
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO ir_attachment ({})
            VALUES {};""".format(
                ", ".join(columns), ", ".join(values)
            ),
        )
    # adapt m2m table
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_group_moderator_rel rel
        SET mail_group_id = mg.id
        FROM mail_group mg
        WHERE mg.old_channel_id = rel.mail_group_id""",
    )
    # fill mail_group_moderation.mail_group_id (field is required)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mail_group_moderation
        ADD COLUMN mail_group_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_group_moderation mgm
        SET mail_group_id = mg.id
        FROM mail_group mg
        WHERE mgm.channel_id = mg.old_channel_id""",
    )
    # fill mail_group_message table
    sql.create_model_table(
        env.cr,
        "mail_group_message",
        columns=[
            ("mail_group_id", "integer", ""),
            ("mail_message_id", "integer", ""),
            ("group_message_parent_id", "integer", ""),
            ("moderator_id", "integer", ""),
            ("moderation_status", "varchar", ""),
            ("create_uid", "integer", ""),
            ("write_uid", "integer", ""),
            ("create_date", "timestamp", ""),
            ("write_date", "timestamp", ""),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mail_group_message (mail_group_id, mail_message_id, moderator_id,
            moderation_status, create_uid, write_uid, create_date, write_date)
        SELECT mg.id, mm.id, mm.moderator_id, mm.moderation_status,
            mm.create_uid, mm.write_uid, mm.create_date, mm.write_date
        FROM mail_message mm
        JOIN mail_message_mail_channel_rel rel ON rel.mail_message_id = mm.id
        JOIN mail_group mg ON rel.mail_channel_id = mg.old_channel_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_group_message mgm
        SET group_message_parent_id = mgm2.id
        FROM mail_message mm
        JOIN mail_message mm2 ON mm.parent_id = mm2.id
        JOIN mail_group_message mgm2 ON mgm2.mail_message_id = mm2.id
        WHERE mgm.mail_message_id = mm.id""",
    )
    # fill mail_group_member table
    sql.create_model_table(
        env.cr,
        "mail_group_member",
        columns=[
            ("email", "varchar", ""),
            ("mail_group_id", "integer", ""),
            ("partner_id", "integer", ""),
            ("create_uid", "integer", ""),
            ("write_uid", "integer", ""),
            ("create_date", "timestamp", ""),
            ("write_date", "timestamp", ""),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO mail_group_member (email, mail_group_id, partner_id,
            create_uid, write_uid, create_date, write_date)
        SELECT rp.email, mg.id, rp.id,
            rel.create_uid, rel.write_uid, rel.create_date, rel.write_date
        FROM res_partner rp
        JOIN mail_channel_partner rel ON rel.partner_id = rp.id
        JOIN mail_group mg ON rel.channel_id = mg.old_channel_id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _copy_columns(env)
    _rename_tables(env)
    _rename_fields(env)
    _delete_channel_follower_records(env)
    delete_obsolete_constraints(env)
    migration_to_mail_group(env)
