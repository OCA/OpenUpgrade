# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xml_ids = [
    'im_livechat.ir_action_client_open_livechat_menu',
    'im_livechat.ir_cron_remove_empty_session',
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, xml_ids)
