# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.load_data(
        cr, 'gamification', 'migrations/9.0.1.0/noupdate_changes.xml')
