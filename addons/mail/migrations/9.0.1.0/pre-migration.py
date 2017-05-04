# -*- coding: utf-8 -*-
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

column_renames = {
    'mail_channel_res_group_rel': [
        ('mail_group_id', 'mail_channel_id'),
    ]
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.update_module_names(
        env.cr, [('email_template', 'mail')], merge_modules=True,
    )
    openupgrade.rename_models(env.cr, model_renames)
    openupgrade.rename_tables(env.cr, table_renames)
    openupgrade.rename_columns(env.cr, column_renames)
    # Remove noupdate ir.rule
    rule = env.ref('mail.mail_group_public_and_joined')
    rule.unlink()
