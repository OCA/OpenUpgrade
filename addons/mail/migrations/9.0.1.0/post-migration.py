# -*- coding: utf-8 -*-
# Copyright 2014 Microcom
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 Eficent - Miquel Raïch
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import uuid
from openupgradelib import openupgrade


def import_data_from_im_chat_module(env):
    """Import data from im_chat module"""
    cr = env.cr
    old_id = openupgrade.get_legacy_name('old_id')
    alias = openupgrade.get_legacy_name('alias_id')

    # Map data from im_chat_session to mail_channel
    cr.execute("""SELECT count(id) FROM im_chat_session""")
    count_sessions = cr.fetchone()
    count_sessions = count_sessions and count_sessions[0] or 0
    for i in range(0, count_sessions, 1):
        cr.execute(
            """
            WITH create_alias as (
                INSERT INTO mail_alias (alias_defaults, alias_contact,
                    alias_model_id, alias_parent_model_id)
                SELECT '{}' AS alias_defaults, 'everyone' AS alias_contact,
                    id, id
                FROM ir_model
                WHERE model = 'mail.channel'
                RETURNING id
            )
            UPDATE im_chat_session ics
            SET %s = create_alias.id
            FROM create_alias
            WHERE ics.id = (SELECT id
                            FROM im_chat_session
                            ORDER BY id ASC
                            LIMIT 1 OFFSET %s)
            """ % (alias, i)
        )
    cr.execute(
        """
        WITH create_channel as (
            INSERT INTO mail_channel (uuid, channel_type, public, alias_id,
                create_uid, create_date, write_uid, write_date, %s, name)
            SELECT uuid, 'chat' as channel_type, 'private' as public, %s,
                create_uid, create_date, write_uid, write_date, id,
                '_dummy_name' as name
            FROM im_chat_session
            RETURNING id
        )
        INSERT INTO mail_followers (channel_id, res_model, res_id)
        SELECT id AS channel_id, 'mail.channel' AS res_model, id AS res_id
        FROM create_channel
        """ % (old_id, alias)
    )
    cr.execute(
        """
        UPDATE mail_alias
        SET alias_force_thread_id = mc.id, alias_parent_thread_id = mc.id
        FROM mail_channel mc
        LEFT JOIN mail_alias ma ON ma.id = mc.alias_id
        WHERE mc.channel_type = 'chat'
        """
    )

    # Map data from im_chat_session_res_users_rel to mail_channel_partner
    cr.execute(
        """
        INSERT INTO mail_channel_partner (partner_id, channel_id, fold_state,
            is_minimized, is_pinned,
            create_uid, create_date, write_uid, write_date)
        SELECT ru.partner_id, mc.id AS channel_id,
            iur.state AS fold_state, FALSE AS is_minimized, TRUE AS is_pinned,
            iur.create_uid, iur.create_date, iur.write_uid, iur.write_date
        FROM im_chat_session_res_users_rel iur
        LEFT JOIN res_users ru ON ru.id = iur.user_id
        LEFT JOIN mail_channel mc ON mc.%s = iur.session_id
        """ % old_id
    )
    cr.execute(
        """
        UPDATE mail_channel mc
        SET name = array_to_string(array(
                            SELECT rp.name
                            FROM mail_channel_partner mcp
                            LEFT JOIN res_partner rp ON mcp.partner_id = rp.id
                            WHERE mcp.channel_id = mc.id
                            ORDER BY rp.name), ', ')
        WHERE mc.name = '_dummy_name'
        """
    )
    cr.execute(
        """
        UPDATE mail_channel mc
        SET group_public_id = rg.id
        FROM res_groups rg
        WHERE rg.name = 'Employee' AND mc.group_public_id IS NULL
        """
    )

    # Map data from im_chat_message to mail_message
    cr.execute(
        """
        SELECT id FROM mail_message_subtype sub
        WHERE sub.default = TRUE AND (
            sub.res_model = 'mail.channel' OR sub.res_model IS NULL)
        ORDER BY id ASC
        LIMIT 1
        """
    )
    subtype_id = cr.fetchone()
    if not subtype_id:
        subtype_id = env["mail.message.subtype"].sudo().create({
            'name': 'Discussions',
            'sequence': '0',
            'hidden': False,
            'default': True,
        }).id
    else:
        subtype_id = subtype_id[0]
    cr.execute(
        """
        INSERT INTO mail_message (author_id, res_id, body, message_type,
            subtype_id, model, record_name, no_auto_thread,
            date,
            create_uid, create_date, write_uid, write_date)
        SELECT ru.partner_id AS author_id, mc.id AS res_id,
            icm.message AS body, CASE
                        WHEN icm.type = 'message' THEN 'comment'
                        WHEN icm.type = 'meta' THEN 'notification'
                        ELSE icm.type
                    END AS message_type, %s AS subtype_id,
            'mail.channel' AS model, mc.name AS record_name, FALSE AS nat,
            icm.create_date,
            icm.create_uid, icm.create_date, icm.write_uid, icm.write_date
        FROM im_chat_message icm
        LEFT JOIN res_users ru ON ru.id = icm.from_id
        LEFT JOIN mail_channel mc ON mc.%s = icm.to_id
        """ % (subtype_id, old_id)
    )


def update_mail_channel_uuid(env):
    channels = env['mail.channel'].sudo().search(
        [('channel_type', '=', 'channel')])
    for channel in channels:
        channel.write({'uuid': uuid.uuid4()})


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    if openupgrade.table_exists(cr, 'im_chat_session'):
        import_data_from_im_chat_module(env)
    # Set partners which will help to see all subscribed channels in
    # Channels sub-menu under Discuss Menu
    cr.execute("""
    INSERT INTO mail_channel_partner (channel_id, partner_id)
    SELECT res_id, partner_id from mail_followers
    WHERE res_model = 'mail.channel'
    AND res_id IN (SELECT id FROM mail_channel);
    """)
    # notifications and stars are plain many2many fields by now
    cr.execute(
        'insert into mail_message_res_partner_needaction_rel '
        '(mail_message_id, res_partner_id) '
        'select distinct message_id, partner_id from mail_notification '
        'where not is_read')
    cr.execute(
        'insert into mail_message_res_partner_starred_rel '
        '(mail_message_id, res_partner_id) '
        'select distinct message_id, partner_id from mail_notification '
        'where starred')
    # make channel listen itself: posting on a channel notifies the channel
    cr.execute(
        """
        INSERT INTO mail_followers (
            res_id, channel_id, res_model
        )
        SELECT id, id, 'mail.channel'
        FROM mail_channel
        WHERE channel_type = 'channel'
        """
    )
    # subscribe the channels to the defaults message subtypes(Discussions)
    cr.execute(
        """
        INSERT INTO mail_followers_mail_message_subtype_rel(
            mail_followers_id, mail_message_subtype_id
        )
        SELECT mf.id, sub.id
        FROM mail_followers mf, mail_message_subtype sub
        WHERE
            mf.res_model='mail.channel'
            and mf.partner_id is null
            and sub.default = TRUE
            and (sub.res_model = 'mail.channel' or sub.res_model is NULL)
        """
    )
    # retrieve messages on channels
    cr.execute(
        """
        INSERT INTO mail_message_mail_channel_rel (
            mail_message_id, mail_channel_id
        )
        SELECT mm.id, mm.res_id
        FROM mail_message mm
        INNER JOIN mail_channel cc on cc.id = mm.res_id
        WHERE mm.model = 'mail.channel'
        """
    )
    cr.execute(
        """
        UPDATE mail_channel
        SET email_send = FALSE
        WHERE email_send IS NULL
        """
    )
    # update uuids because in the model rename they got the same default uuid
    update_mail_channel_uuid(env)
    openupgrade.load_data(
        cr, 'mail', 'migrations/9.0.1.0/noupdate_changes.xml',
    )
