# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "payment_stripe.action_payment_acquirer_onboarding",
        "payment_stripe.action_payment_provider_onboarding",
    ),
    (
        "payment_stripe.payment_acquirer_form",
        "payment_stripe.payment_provider_form",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
