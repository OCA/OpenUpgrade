# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _fill_payment_method(env):
    PaymentToken = env["payment.token"].with_context(active_test=False)
    PaymentTransaction = env["payment.transaction"].with_context(active_test=False)
    PaymentMethod = env["payment.method"].with_context(active_test=False)

    for payment_token in PaymentToken.search([("payment_method_id", "=", False)]):
        payment_token.payment_method_id = (
            PaymentMethod._get_from_code(payment_token.provider_id.code)
            or payment_token.provider_id.payment_method_ids[:1]
        ).id

    for transaction in PaymentTransaction.search([("payment_method_id", "=", False)]):
        transaction.payment_method_id = (
            PaymentMethod._get_from_code(transaction.provider_id.code)
            or transaction.provider_id.payment_method_ids[:1]
        ).id


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "payment", "17.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, ["payment.payment_transaction_user_rule"]
    )
    _fill_payment_method(env)
