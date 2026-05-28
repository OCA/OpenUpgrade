from openupgradelib import openupgrade

_renamed_fields = [
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_api_key",
        "viva_com_api_key",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_bearer_token",
        "viva_com_bearer_token",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_client_id",
        "viva_com_client_id",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_client_secret",
        "viva_com_client_secret",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_latest_response",
        "viva_com_latest_response",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_merchant_id",
        "viva_com_merchant_id",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_terminal_id",
        "viva_com_terminal_id",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_test_mode",
        "viva_com_test_mode",
    ),
    (
        "pos.payment.method",
        "pos_payment_method",
        "viva_wallet_webhook_verification_key",
        "viva_com_webhook_verification_key",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _renamed_fields)
