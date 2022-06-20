from openupgradelib import openupgrade


def convert_payment_acquirer_provider(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_acquirer
        SET provider = 'none'
        WHERE provider = 'manual'""",
    )


def fill_payment_transaction_last_state_change(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_transaction
        SET last_state_change = write_date
        WHERE last_state_change IS NULL
        """,
    )


def fill_payment_transaction_partner_state_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_transaction pt
        SET partner_state_id = rp.state_id
        FROM res_partner rp
        WHERE rp.id = pt.partner_id
            AND rp.state_id IS NOT NULL
            AND partner_state_id IS NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "payment", "15.0.2.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "payment",
        [
            "payment_acquirer_adyen",
            "payment_acquirer_alipay",
            "payment_acquirer_payulatam",
            "payment_acquirer_sepa_direct_debit",
            "payment_acquirer_stripe",
            "payment_token_user_rule",
            "payment_transaction_billing_rule",
            "payment_transaction_user_rule",
        ],
    )
    convert_payment_acquirer_provider(env)
    fill_payment_transaction_partner_state_id(env)
    fill_payment_transaction_last_state_change(env)
