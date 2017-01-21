# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


xmlid_renames = [
    ('im_livechat.group_im_livechat', 'im_livechat.im_livechat_group_user'),
    ('im_livechat.group_im_livechat_manager',
     'im_livechat.im_livechat_group_manager'),
]

column_renames = {
    'im_livechat_channel': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)
    openupgrade.rename_columns(cr, column_renames)
