# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        (
            "payment.provider",
            "payment_provider",
            "redsys_terminal",
            "redsys_merchant_terminal",
        ),
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "payment_redsys.provider_form_redsys",
                "payment_redsys.payment_provider_form",
            ),
            ("payment_redsys.redsys_form", "payment_redsys.redirect_form"),
        ],
    )
