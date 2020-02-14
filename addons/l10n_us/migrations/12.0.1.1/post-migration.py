# Copyright 2020 ForgeFLow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_res_partner_bank_aba_routing(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE res_partner_bank
        SET aba_routing = '' || %s
        WHERE %s IS NOT NULL
        """, (openupgrade.get_legacy_name('aba_routing'),
              openupgrade.get_legacy_name('aba_routing'))
    )


@openupgrade.migrate()
def migrate(env, version):
    map_res_partner_bank_aba_routing(env)
