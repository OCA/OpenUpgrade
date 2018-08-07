# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from openupgradelib import openupgrade_90


attachment_fields = {
    'im_livechat.channel': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
}


def import_data_from_im_chat(cr):
    """Import data from im_chat module"""
    cr.execute(
        """
        UPDATE mail_channel mc
        SET livechat_channel_id = ics.channel_id,
            anonymous_name = ics.anonymous_name
        FROM im_chat_session ics
        WHERE mc.%s = ics.id
        """ % openupgrade.get_legacy_name('old_id')
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade_90.convert_binary_field_to_attachment(env, attachment_fields)
    if openupgrade.table_exists(env.cr, 'im_chat_session'):
        import_data_from_im_chat(env.cr)
