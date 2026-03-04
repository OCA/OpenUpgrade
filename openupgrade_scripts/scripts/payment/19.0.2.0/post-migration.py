# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_deleted_xmlids = [
    "payment.payment_method_axis",
    "payment.payment_method_bancomat_pay",
    "payment.payment_method_bpi",
    "payment.payment_method_brankas",
    "payment.payment_method_dolfin",
    "payment.payment_method_frafinance",
    "payment.payment_method_giropay",
    "payment.payment_method_gsb",
    "payment.payment_method_lydia",
    "payment.payment_method_lyfpay",
    "payment.payment_method_naver_pay",
    "payment.payment_method_pay_easy",
    "payment.payment_method_paylib",
    "payment.payment_method_paypay",
    "payment.payment_method_payu",
    "payment.payment_method_toss_pay",
    "payment.onboarding_onboarding_step_payment_provider",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "payment", "19.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
