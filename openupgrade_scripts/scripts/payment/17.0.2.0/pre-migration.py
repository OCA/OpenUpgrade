# Copyright 2024 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "payment.action_payment_icon",
        "payment.action_payment_method",
    ),
    (
        "payment.payment_icon_cc_visa",
        "payment.payment_method_visa",
    ),
    (
        "payment.payment_icon_cc_mastercard",
        "payment.payment_method_mastercard",
    ),
    (
        "payment.payment_icon_cc_american_express",
        "payment.payment_method_amex",
    ),
    (
        "payment.payment_icon_cc_discover",
        "payment.payment_method_discover",
    ),
    (
        "payment.payment_icon_cc_diners_club_intl",
        "payment.payment_method_diners",
    ),
    (
        "payment.payment_icon_paypal",
        "payment.payment_method_paypal",
    ),
    (
        "payment.payment_icon_cc_rupay",
        "payment.payment_method_rupay",
    ),
    # This one has been removed with https://github.com/odoo/odoo/pull/140907
    # (
    #     "payment.payment_icon_apple_pay",
    #     "payment.payment_method_apple_pay",
    # ),
    (
        "payment.payment_icon_cc_jcb",
        "payment.payment_method_jcb",
    ),
    (
        "payment.payment_icon_cc_maestro",
        "payment.payment_method_maestro",
    ),
    (
        "payment.payment_icon_cc_cirrus",
        "payment.payment_method_cirrus",
    ),
    (
        "payment.payment_icon_cc_unionpay",
        "payment.payment_method_unionpay",
    ),
    (
        "payment.payment_icon_cc_bancontact",
        "payment.payment_method_bancontact",
    ),
    # This one has been removed with https://github.com/odoo/odoo/pull/140907
    # (
    #     "payment.payment_icon_cc_western_union",
    #     "payment.payment_method_western_union",
    # ),
    (
        "payment.payment_icon_sepa",
        "payment.payment_method_sepa_direct_debit",
    ),
    (
        "payment.payment_icon_cc_ideal",
        "payment.payment_method_ideal",
    ),
    # This one has been removed with https://github.com/odoo/odoo/pull/120446
    #
    # (
    #     "payment.payment_icon_cc_webmoney",
    #     "payment.payment_method_webmoney",
    # ),
    (
        "payment.payment_icon_cc_giropay",
        "payment.payment_method_giropay",
    ),
    (
        "payment.payment_icon_cc_eps",
        "payment.payment_method_eps",
    ),
    (
        "payment.payment_icon_cc_p24",
        "payment.payment_method_p24",
    ),
    (
        "payment.payment_icon_cc_codensa_easy_credit",
        "payment.payment_method_codensa",
    ),
    (
        "payment.payment_icon_kbc",
        "payment.payment_method_kbc_cbc",
    ),
    (
        "payment.payment_icon_mpesa",
        "payment.payment_method_mpesa",
    ),
    # This one has been removed with https://github.com/odoo/odoo/pull/120446
    # (
    #     "payment.payment_icon_airtel_money",
    #     "payment.payment_method_airtel_money",
    # ),
    (
        "payment.payment_icon_mtn_mobile_money",
        "payment.payment_method_mobile_money",
    ),
    (
        "payment.payment_icon_barter_by_flutterwave",
        "payment.payment_method_ussd",
    ),
    # This one has been removed with https://github.com/odoo/odoo/pull/120446
    # (
    #     "payment.payment_icon_sadad",
    #     "payment.payment_method_sadad",
    # ),
    (
        "payment.payment_icon_mada",
        "payment.payment_method_mada",
    ),
    # These ones have been removed with https://github.com/odoo/odoo/pull/120446
    # (
    #     "payment.payment_icon_bbva_bancomer",
    #     "payment.payment_method_bbva_bancomer",
    # ),
    # (
    #     "payment.payment_icon_citibanamex",
    #     "payment.payment_method_citibanamex",
    # ),
]

_model_renames = [
    ("payment.icon", "payment.method"),
]

_table_renames = [
    ("payment_icon", "payment_method"),
    ("payment_icon_payment_provider_rel", "payment_method_payment_provider_rel"),
]

_column_renames = {
    "payment_method_payment_provider_rel": [
        ("payment_icon_id", "payment_method_id"),
    ],
}

_field_renames = [
    (
        "payment.provider",
        "payment_provider",
        "payment_icon_ids",
        "payment_method_ids",
    ),
]

_noupdate_xmlids = [
    "payment_method_visa",
    "payment_method_mastercard",
    "payment_method_amex",
    "payment_method_discover",
    "payment_method_diners",
    "payment_method_paypal",
    "payment_method_rupay",
    "payment_method_jcb",
    "payment_method_maestro",
    "payment_method_cirrus",
    "payment_method_unionpay",
    "payment_method_bancontact",
    "payment_method_sepa_direct_debit",
    "payment_method_ideal",
    "payment_method_giropay",
    "payment_method_eps",
    "payment_method_p24",
    "payment_method_codensa",
    "payment_method_kbc_cbc",
    "payment_method_mpesa",
    "payment_method_mobile_money",
    "payment_method_ussd",
    "payment_method_mada",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.set_xml_ids_noupdate_value(env, "payment", _noupdate_xmlids, True)
