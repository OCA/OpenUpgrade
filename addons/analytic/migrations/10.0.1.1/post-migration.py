# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def deactivate_closed_accounts(cr):
    # not using sql to restore account_type but map values
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('account_type'),
        'active',  [('closed',  False), ('normal', True)],
        table='account_analytic_account',
        write='sql'
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    deactivate_closed_accounts(cr)
