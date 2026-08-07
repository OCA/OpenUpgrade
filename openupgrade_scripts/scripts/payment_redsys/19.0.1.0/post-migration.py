# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo import Command

PAY_METHOD_MAPPING = {
    "T": "payment.payment_method_card",
    "z": "payment.payment_method_bizum",
}


def _adjust_payment_methods(env):
    """On the OCA module, done before the payment refactoring, the payment method of
    Redsys was defined through a specific field, instead of using payment_method_ids
    field.

    We need to convert existing payment providers to this new way, as the Odoo module
    handles it through it.
    """
    if not openupgrade.column_exists(env.cr, "payment_provider", "redsys_pay_method"):
        return  # No previous OCA module installed
    env.cr.execute(
        "SELECT id, redsys_pay_method FROM payment_provider "
        "WHERE code='redsys' AND redsys_pay_method IS NOT NULL"
    )
    for provider_id, redsys_pay_method in env.cr.fetchall():
        provider = env["payment.provider"].browse(provider_id)
        provider.payment_method_ids = [
            Command.set(env.ref(PAY_METHOD_MAPPING[redsys_pay_method]).ids)
        ]


@openupgrade.migrate()
def migrate(env, version):
    _adjust_payment_methods(env)
