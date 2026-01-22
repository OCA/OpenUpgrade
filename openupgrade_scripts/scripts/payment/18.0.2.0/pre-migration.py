# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_xmlid_renames = [
    ("website_payment.action_activate_stripe", "payment.action_activate_stripe"),
    ("payment.payment_method_emi", "payment.payment_method_emi_india"),
    (
        "payment_worldline.payment_method_alipay_plus",
        "payment.payment_method_alipay_plus",
    ),
    (
        "payment_worldline.payment_method_post_finance",
        "payment.payment_method_post_finance",
    ),
    (
        "payment_worldline.payment_provider_worldline",
        "payment.payment_provider_worldline",
    ),
]


def fill_payment_support_refund(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_method
        SET support_refund = 'none'
        WHERE support_refund IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fill_payment_support_refund(env)
