# -*- coding: utf-8 -*-
# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'website_crm', 'migrations/10.0.2.0/noupdate_changes.xml',
    )
