# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('marketing.campaign.activity', 'marketing_campaign_activity', 'type',
     'action_type'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
