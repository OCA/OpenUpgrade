# Copyright 2023 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_model_renames = [
    ("payment.acquirer", "payment.provider"),
]

_table_renames = [
    ("payment_acquirer", "payment_provider"),
    ("payment_acquirer_payment_icon_rel", "payment_provider_payment_icon_rel"),
]

_field_renames = [
    (
        "account.payment.method.line",
        "account_payment_method_line",
        "payment_acquirer_id",
        "payment_provider_id",
    ),
    (
        "account.payment.method.line",
        "account_payment_method_line",
        "payment_acquirer_state",
        "payment_provider_state",
    ),
    (
        "payment.icon",
        "payment_icon",
        "acquirer_ids",
        "provider_ids",
    ),
    (
        "payment.token",
        "payment_token",
        "acquirer_id",
        "provider_id",
    ),
    (
        "payment.token",
        "payment_token",
        "acquirer_ref",
        "provider_ref",
    ),
    (
        "payment.token",
        "payment_token",
        "name",
        "payment_details",
    ),
    (
        "payment.transaction",
        "payment_transaction",
        "acquirer_id",
        "provider_id",
    ),
    (
        "payment.transaction",
        "payment_transaction",
        "acquirer_reference",
        "provider_reference",
    ),
    (
        "res.company",
        "res_company",
        "payment_acquirer_onboarding_state",
        "payment_provider_onboarding_state",
    ),
]

_columns_copies = {
    "payment_provider": [("provider", "code", "varchar")],
}

_xmlid_renames = [
    (
        "payment.action_invoice_order_generate_link",
        "account_payment.action_invoice_order_generate_link",
    ),
    (
        "payment.action_payment_acquirer",
        "payment.action_payment_provider",
    ),
    (
        "payment.payment_acquirer_onboarding_wizard",
        "payment.payment_provider_onboarding_wizard",
    ),
    (
        "payment.payment_acquirer_system",
        "payment.payment_provider_system",
    ),
    (
        "payment.payment_link_wizard",
        "account_payment.payment_link_wizard",
    ),
    (
        "payment.payment_refund_wizard",
        "account_payment.payment_refund_wizard",
    ),
    (
        "payment.payment_acquirer_company_rule",
        "payment.payment_provider_company_rule",
    ),
    (
        "payment.payment_token_billing_rule",
        "account_payment.payment_token_billing_rule",
    ),
    (
        "payment.payment_transaction_billing_rule",
        "account_payment.payment_transaction_billing_rule",
    ),
    (
        "payment.payment_acquirer_menu",
        "account_payment.payment_provider_menu",
    ),
    (
        "payment.payment_icon_menu",
        "account_payment.payment_icon_menu",
    ),
    (
        "payment.payment_token_menu",
        "account_payment.payment_token_menu",
    ),
    (
        "payment.payment_transaction_menu",
        "account_payment.payment_transaction_menu",
    ),
    (
        "payment.account_invoice_view_form_inherit_payment",
        "account_payment.account_invoice_view_form_inherit_payment",
    ),
    (
        "payment.payment_acquirer_form",
        "account_payment.payment_provider_form",
    ),
    (
        "payment.payment_acquirer_kanban",
        "account_payment.payment_provider_kanban",
    ),
    (
        "payment.payment_acquirer_list",
        "account_payment.payment_provider_list",
    ),
    (
        "payment.payment_acquirer_onboarding_wizard_form",
        "payment.payment_provider_onboarding_wizard_form",
    ),
    (
        "payment.payment_acquirer_search",
        "account_payment.payment_provider_search",
    ),
    (
        "payment.payment_refund_wizard_view_form",
        "account_payment.payment_refund_wizard_view_form",
    ),
    (
        "payment.view_account_journal_form",
        "account_payment.view_account_journal_form",
    ),
    (
        "payment.view_account_payment_form_inherit_payment",
        "account_payment.view_account_payment_form_inherit_payment",
    ),
    (
        "payment.view_account_payment_register_form_inherit_payment",
        "account_payment.view_account_payment_register_form_inherit_payment",
    ),
    (
        "payment.payment_acquirer_adyen",
        "payment.payment_provider_adyen",
    ),
    (
        "payment.payment_acquirer_authorize",
        "payment.payment_provider_authorize",
    ),
    (
        "payment.payment_acquirer_buckaroo",
        "payment.payment_provider_buckaroo",
    ),
    (
        "payment.payment_acquirer_mollie",
        "payment.payment_provider_mollie",
    ),
    (
        "payment.payment_acquirer_paypal",
        "payment.payment_provider_paypal",
    ),
    (
        "payment.payment_acquirer_sepa_direct_debit",
        "payment.payment_provider_sepa_direct_debit",
    ),
    (
        "payment.payment_acquirer_sips",
        "payment.payment_provider_sips",
    ),
    (
        "payment.payment_acquirer_stripe",
        "payment.payment_provider_stripe",
    ),
    (
        "payment.payment_acquirer_test",
        "payment.payment_provider_test",
    ),
    (
        "payment.payment_acquirer_transfer",
        "payment.payment_provider_transfer",
    ),
]


def _module_account_payment_to_install(env):
    """
    This function force installation of account_payment in case it is not yet installed
    In v16, account_payment is auto_install = ["account"] (it was not in v15)
    Since migration of payment module moves fields to account_payment, if the latter
    is not installed you will get a JS error when trying to access account moves
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_module_module
        SET state = 'to install'
        WHERE name = 'account_payment' AND state = 'uninstalled'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.copy_columns(env.cr, _columns_copies)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    _module_account_payment_to_install(env)
