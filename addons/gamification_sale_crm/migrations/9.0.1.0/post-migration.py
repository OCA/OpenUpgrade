# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Remove xml record related to non existent model crm_phonecall
    env.ref('gamification_sale_crm.definition_crm_nbr_call').unlink()
    openupgrade.load_data(
        env.cr,
        'gamification_sale_crm',
        'migrations/9.0.1.0/noupdate_changes.xml',
    )
