from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "payment.acquirer",
                "payment_acquirer",
                "brq_secretkey",
                "buckaroo_secret_key",
            ),
            (
                "payment.acquirer",
                "payment_acquirer",
                "brq_websitekey",
                "buckaroo_website_key",
            ),
        ],
    )
