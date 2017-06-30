# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('timesheet_range'),
        'timesheet_range', [('day', 'month')], table='res_company',
    )
