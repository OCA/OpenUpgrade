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


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_models(env.cr, model_renames)
    openupgrade.rename_tables(env.cr, table_renames)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.rename_columns(env.cr, column_renames)
    # Remove noupdate ir.rule
    rule = env.ref('mail.mail_group_public_and_joined')
    rule.unlink()
