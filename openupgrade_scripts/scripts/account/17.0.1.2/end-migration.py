# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _res_partner_bank_computation(env):
    partner_banks = env["res.partner.bank"].with_context(active_test=False).search([])
    partner_banks._compute_display_account_warning()


@openupgrade.migrate()
def migrate(env, version):
    _res_partner_bank_computation(env)
