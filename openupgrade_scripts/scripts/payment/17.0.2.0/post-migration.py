# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _fill_payment_method(env):
    PaymentProvider = env["payment.provider"]
    PaymentToken = env["payment.token"].with_context(active_test=False)
    PaymentTransaction = env["payment.transaction"].with_context(active_test=False)
    PaymentMethod = env["payment.method"].with_context(active_test=False)

    unknown_payment_method = env.ref("payment.payment_method_unknown")

    for group in PaymentToken.read_group(
        [("payment_method_id", "=", False)], ["provider_id"], ["provider_id"]
    ):
        provider = PaymentProvider.browse(group["provider_id"][0])
        PaymentToken.search(group["__domain"]).write(
            {
                "payment_method_id": (
                    PaymentMethod._get_from_code(provider.code)
                    or unknown_payment_method
                ).id,
            }
        )

    for group in PaymentTransaction.read_group(
        [("payment_method_id", "=", False)], ["provider_id"], ["provider_id"]
    ):
        provider = PaymentProvider.browse(group["provider_id"][0])
        PaymentTransaction.search(group["__domain"]).write(
            {
                "payment_method_id": (
                    PaymentMethod._get_from_code(provider.code)
                    or unknown_payment_method
                ).id
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "payment", "17.0.2.0/noupdate_changes_work.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, ["payment.payment_transaction_user_rule"]
    )
    _fill_payment_method(env)
