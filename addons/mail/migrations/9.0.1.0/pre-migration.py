# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

model_renames = [
    ('mail.group', 'mail.channel'),
    ('email.template', 'mail.template'),
]

table_renames = [
    ('mail_group', 'mail_channel'),
    ('email_template', 'mail_template'),
    ('mail_group_res_group_rel', 'mail_channel_res_group_rel'),
]

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('mail.message', 'mail_message', 'type', 'message_type'),
]

column_renames = {
    'mail_channel_res_group_rel': [
        ('mail_group_id', 'mail_channel_id'),
    ]
}

xmlid_renames = [
    ('mail.group_all_employees', 'mail.channel_all_employees'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_models(env.cr, model_renames)
    openupgrade.rename_tables(env.cr, table_renames)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.rename_columns(env.cr, column_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
    # Remove noupdate records
    xml_ids = [
        'mail_group_public_and_joined',
        'mail_followers_read_write_others',
        'mail_notification_read_write_own',
        'ir_cron_mail_garbage_collect_attachments',
    ]
    for xml_id in xml_ids:
        rule = env.ref('mail.' + xml_id, False)
        if rule:
            rule.unlink()

    if openupgrade.table_exists(env.cr, 'im_chat_session'):
        env.cr.execute(
            """
            ALTER TABLE mail_channel
            ADD COLUMN %s integer;
            """ % openupgrade.get_legacy_name('old_id')
        )
        env.cr.execute(
            """
            ALTER TABLE im_chat_session
            ADD COLUMN %s integer;
            """ % openupgrade.get_legacy_name('alias_id')
        )
