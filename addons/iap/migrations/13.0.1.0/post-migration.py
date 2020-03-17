# Copyright 2020 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _field_type_change(env):
    openupgrade.m2o_to_x2m(
        env.cr,
        env['iap.account'], 'iap_account',
        'company_ids', openupgrade.get_legacy_name('company_id')
    )


@openupgrade.migrate()
def migrate(env, version):
    _field_type_change(env)
