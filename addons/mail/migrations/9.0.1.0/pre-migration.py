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


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.update_module_names(
        cr, [('email_template', 'mail')], merge_modules=True,
    )
    openupgrade.rename_models(cr, model_renames)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    # with this, the rule and the xmlid will be cleaned up at the end of
    # the migration
    cr.execute(
        'update ir_model_data set noupdate=False where '
        "module='mail' and name='mail_group_public_and_joined'")
