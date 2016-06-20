# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
import logging
logger = logging.getLogger('OpenUpgrade.stock')

table_renames = [('mail_group', 'mail_channel'),
                 ('email_template', 'mail_template'),
                 ('mail_group_res_group_rel', 'mail_channel_res_group_rel'),
                 ]

column_renames = {
    'mail_channel_res_group_rel': [('mail_group_id', 'mail_channel_id'),
                                   ]
}


def set_mail_channel(cr):
    # change model as 'mail.channel' for 'mail.group' 
    cr.execute("""
    UPDATE mail_message SET model = 'mail.channel' WHERE model = 'mail.group'
    """)

    cr.execute("""
    UPDATE mail_followers SET res_model = 'mail.channel' WHERE res_model = 'mail.group'
    """)


@openupgrade.migrate()
def migrate(cr, version):

    openupgrade.logged_query(cr, """
        DELETE FROM ir_ui_view v
        USING ir_model_data d
        WHERE v.id=d.res_id
        AND d.module = 'email_template'
        AND d.model = 'ir.ui.view'
        """)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    set_mail_channel(cr)
