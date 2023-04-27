from openupgradelib import openupgrade

_copied_columns = {
    "payment_acquirer": [
        ("provider", None, None),
    ],
}

_renamed_fields = [
    (
        "payment.token",
        "payment_token",
        "payment_ids",
        "transaction_ids",
    ),
    (
        "payment.transaction",
        "payment_transaction",
        "is_processed",
        "is_post_processed",
    ),
    (
        "payment.transaction",
        "payment_transaction",
        "payment_token_id",
        "token_id",
    ),
    (
        "payment.acquirer",
        "payment_acquirer",
        "registration_view_template_id",
        "inline_form_view_id",
    ),
]

_renamed_xmlids = [
    ("payment.payment_token_salesman_rule", "payment.payment_token_billing_rule"),
    ("payment.payment_acquirer_ingenico", "payment.payment_acquirer_ogone"),
    ("payment.payment_acquirer_payu", "payment.payment_acquirer_payumoney"),
]


def fill_payment_token_name(env):
    # field it's required now
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_token
        SET name = 'XXXXXXXXXXXX????'
        WHERE name IS NULL""",
    )


def fill_payment_transaction_partner_id(env):
    # field it's required now
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_transaction pt
        SET partner_id = COALESCE(ap.partner_id, rc.partner_id)
        FROM account_payment ap
        JOIN account_move am ON ap.move_id = am.id
        JOIN account_journal aj ON am.journal_id = aj.id
        JOIN res_company rc ON aj.company_id = rc.id
        WHERE pt.partner_id IS NULL
            AND ap.payment_token_id = pt.token_id
            AND (ap.payment_transaction_id = pt.id OR pt.payment_id = ap.id)""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_transaction pt
        SET partner_id = COALESCE(ap.partner_id, rc.partner_id)
        FROM account_payment ap
        JOIN account_move am ON ap.move_id = am.id
        JOIN account_journal aj ON am.journal_id = aj.id
        JOIN res_company rc ON aj.company_id = rc.id
        WHERE pt.partner_id IS NULL
            AND (ap.payment_transaction_id = pt.id OR pt.payment_id = ap.id)""",
    )


def delete_payment_adquirer_inline_form_view_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_acquirer pa
        SET inline_form_view_id = NULL
        WHERE payment_flow = 'form'""",
    )


def convert_payment_acquirer_provider(env):
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE payment_acquirer
        SET provider = 'none'
        WHERE {openupgrade.get_legacy_name('provider')} = 'manual'""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _copied_columns)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
    convert_payment_acquirer_provider(env)
    fill_payment_token_name(env)
    fill_payment_transaction_partner_id(env)
    delete_payment_adquirer_inline_form_view_id(env)
