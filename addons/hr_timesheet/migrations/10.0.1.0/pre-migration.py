# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

COLUMN_RENAMES = {
    'account_analytic_account': [
        ('use_timesheets', None),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, COLUMN_RENAMES)
