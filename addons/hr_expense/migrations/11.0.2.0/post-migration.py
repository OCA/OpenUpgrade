# -*- coding: utf-8 -*-
# Copyright 2017 Le Filament (<https://le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    openupgrade.load_data(
        cr, 'hr_expense', 'migrations/11.0.2.0/noupdate_changes.xml')
