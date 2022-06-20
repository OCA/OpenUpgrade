from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "payment.transaction",
                "payment_transaction",
                "paypal_txn_type",
                "paypal_type",
            ),
        ],
    )
