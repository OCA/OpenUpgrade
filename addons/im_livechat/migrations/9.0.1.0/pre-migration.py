# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


xmlid_renames = [
    ('im_livechat.group_im_livechat', 'im_livechat.im_livechat_group_user'),
    ('im_livechat.group_im_livechat_manager',
     'im_livechat.im_livechat_group_manager'),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)
