# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo import Command

_PROVIDER_CODE_MAPPING = {
    "adyen": "payment.payment_provider_adyen",
    "alipay": "payment_alipay.payment_provider_alipay",
    "aps": "payment.payment_provider_aps",
    "asiapay": "payment.payment_provider_asiapay",
    "authorize": "payment.payment_provider_authorize",
    "buckaroo": "payment.payment_provider_buckaroo",
    # This one should be handled in payment_custom OpenUpgrade script
    # "custom": "payment.payment_provider_transfer",
    # This one should be handled in payment_demo OpenUpgrade script
    # "demo": "payment.payment_provider_demo",
    "flutterwave": "payment.payment_provider_flutterwave",
    "mercado_pago": "payment.payment_provider_mercado_pago",
    "mollie": "payment.payment_provider_mollie",
    "ogone": "payment_ogone.payment_provider_ogone",
    "paypal": "payment.payment_provider_paypal",
    "payulatam": "payment_payulatam.payment_provider_payulatam",
    "payumoney": "payment_payumoney.payment_provider_payumoney",
    "razorpay": "payment.payment_provider_razorpay",
    "sips": "payment.payment_provider_sips",
    "stripe": "payment.payment_provider_stripe",
    "xendit": "payment.payment_provider_xendit",
}


def _get_provider_payment_method(env):
    return {
        "payment.payment_provider_adyen": [
            Command.set(
                [
                    env.ref("payment.payment_method_ach_direct_debit").id,
                    env.ref("payment.payment_method_affirm").id,
                    env.ref("payment.payment_method_afterpay").id,
                    env.ref("payment.payment_method_alipay").id,
                    env.ref("payment.payment_method_alipay_hk").id,
                    env.ref("payment.payment_method_alma").id,
                    env.ref("payment.payment_method_bacs_direct_debit").id,
                    env.ref("payment.payment_method_bancontact").id,
                    env.ref("payment.payment_method_benefit").id,
                    env.ref("payment.payment_method_bizum").id,
                    env.ref("payment.payment_method_blik").id,
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_cash_app_pay").id,
                    env.ref("payment.payment_method_clearpay").id,
                    env.ref("payment.payment_method_dana").id,
                    env.ref("payment.payment_method_duitnow").id,
                    env.ref("payment.payment_method_elo").id,
                    env.ref("payment.payment_method_eps").id,
                    env.ref("payment.payment_method_fpx").id,
                    env.ref("payment.payment_method_gcash").id,
                    env.ref("payment.payment_method_giropay").id,
                    env.ref("payment.payment_method_gopay").id,
                    env.ref("payment.payment_method_hipercard").id,
                    env.ref("payment.payment_method_ideal").id,
                    env.ref("payment.payment_method_kakaopay").id,
                    env.ref("payment.payment_method_klarna").id,
                    env.ref("payment.payment_method_klarna_paynow").id,
                    env.ref("payment.payment_method_klarna_pay_over_time").id,
                    env.ref("payment.payment_method_knet").id,
                    env.ref("payment.payment_method_mbway").id,
                    env.ref("payment.payment_method_mobile_pay").id,
                    env.ref("payment.payment_method_momo").id,
                    env.ref("payment.payment_method_multibanco").id,
                    env.ref("payment.payment_method_napas_card").id,
                    env.ref("payment.payment_method_online_banking_czech_republic").id,
                    env.ref("payment.payment_method_online_banking_india").id,
                    env.ref("payment.payment_method_online_banking_slovakia").id,
                    env.ref("payment.payment_method_online_banking_thailand").id,
                    env.ref("payment.payment_method_open_banking").id,
                    env.ref("payment.payment_method_p24").id,
                    env.ref("payment.payment_method_paybright").id,
                    env.ref("payment.payment_method_paysafecard").id,
                    env.ref("payment.payment_method_paynow").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_paytm").id,
                    env.ref("payment.payment_method_paytrail").id,
                    env.ref("payment.payment_method_pix").id,
                    env.ref("payment.payment_method_promptpay").id,
                    env.ref("payment.payment_method_ratepay").id,
                    env.ref("payment.payment_method_samsung_pay").id,
                    env.ref("payment.payment_method_sepa_direct_debit").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_swish").id,
                    env.ref("payment.payment_method_touch_n_go").id,
                    env.ref("payment.payment_method_trustly").id,
                    env.ref("payment.payment_method_twint").id,
                    env.ref("payment.payment_method_upi").id,
                    env.ref("payment.payment_method_vipps").id,
                    env.ref("payment.payment_method_wallets_india").id,
                    env.ref("payment.payment_method_walley").id,
                    env.ref("payment.payment_method_wechat_pay").id,
                    env.ref("payment.payment_method_zip").id,
                ]
            )
        ],
        "payment_alipay.payment_provider_alipay": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_rabbit_line_pay").id,
                    env.ref("payment.payment_method_truemoney").id,
                    env.ref("payment.payment_method_boost").id,
                    env.ref("payment.payment_method_touch_n_go").id,
                    env.ref("payment.payment_method_gcash").id,
                    env.ref("payment.payment_method_billease").id,
                    env.ref("payment.payment_method_bpi").id,
                    env.ref("payment.payment_method_maya").id,
                    env.ref("payment.payment_method_dana").id,
                    env.ref("payment.payment_method_akulaku").id,
                    env.ref("payment.payment_method_kredivo").id,
                    env.ref("payment.payment_method_kakaopay").id,
                    env.ref("payment.payment_method_naver_pay").id,
                    env.ref("payment.payment_method_toss_pay").id,
                    env.ref("payment.payment_method_alipay").id,
                    env.ref("payment.payment_method_alipay_hk").id,
                    env.ref("payment.payment_method_dolfin").id,
                    env.ref("payment.payment_method_grabpay").id,
                    env.ref("payment.payment_method_gopay").id,
                    env.ref("payment.payment_method_linkaja").id,
                    env.ref("payment.payment_method_ovo").id,
                    env.ref("payment.payment_method_paypay").id,
                    env.ref("payment.payment_method_zalopay").id,
                    env.ref("payment.payment_method_bangkok_bank").id,
                    env.ref("payment.payment_method_bank_of_ayudhya").id,
                    env.ref("payment.payment_method_krungthai_bank").id,
                    env.ref("payment.payment_method_scb").id,
                    env.ref("payment.payment_method_blik").id,
                    env.ref("payment.payment_method_gsb").id,
                    env.ref("payment.payment_method_kasikorn_bank").id,
                    env.ref("payment.payment_method_promptpay").id,
                    env.ref("payment.payment_method_paynow").id,
                    env.ref("payment.payment_method_bni").id,
                    env.ref("payment.payment_method_mandiri").id,
                    env.ref("payment.payment_method_maybank").id,
                    env.ref("payment.payment_method_cimb_niaga").id,
                    env.ref("payment.payment_method_bsi").id,
                    env.ref("payment.payment_method_qris").id,
                    env.ref("payment.payment_method_pix").id,
                    env.ref("payment.payment_method_bancontact").id,
                    env.ref("payment.payment_method_giropay").id,
                    env.ref("payment.payment_method_ideal").id,
                    env.ref("payment.payment_method_payu").id,
                    env.ref("payment.payment_method_p24").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_eps").id,
                    env.ref("payment.payment_method_bancomat_pay").id,
                    env.ref("payment.payment_method_brankas").id,
                    env.ref("payment.payment_method_pay_easy").id,
                    env.ref("payment.payment_method_fpx").id,
                ]
            )
        ],
        "payment.payment_provider_aps": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_mada").id,
                    env.ref("payment.payment_method_knet").id,
                    env.ref("payment.payment_method_meeza").id,
                    env.ref("payment.payment_method_naps").id,
                    env.ref("payment.payment_method_omannet").id,
                    env.ref("payment.payment_method_benefit").id,
                ]
            )
        ],
        "payment.payment_provider_asiapay": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_alipay").id,
                    env.ref("payment.payment_method_wechat_pay").id,
                    env.ref("payment.payment_method_poli").id,
                    env.ref("payment.payment_method_afterpay").id,
                    env.ref("payment.payment_method_clearpay").id,
                    env.ref("payment.payment_method_humm").id,
                    env.ref("payment.payment_method_zip").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_atome").id,
                    env.ref("payment.payment_method_pace").id,
                    env.ref("payment.payment_method_shopback").id,
                    env.ref("payment.payment_method_grabpay").id,
                    env.ref("payment.payment_method_samsung_pay").id,
                    env.ref("payment.payment_method_hoolah").id,
                    env.ref("payment.payment_method_boost").id,
                    env.ref("payment.payment_method_duitnow").id,
                    env.ref("payment.payment_method_touch_n_go").id,
                    env.ref("payment.payment_method_bancnet").id,
                    env.ref("payment.payment_method_gcash").id,
                    env.ref("payment.payment_method_paynow").id,
                    env.ref("payment.payment_method_linepay").id,
                    env.ref("payment.payment_method_bangkok_bank").id,
                    env.ref("payment.payment_method_krungthai_bank").id,
                    env.ref("payment.payment_method_uob").id,
                    env.ref("payment.payment_method_scb").id,
                    env.ref("payment.payment_method_bank_of_ayudhya").id,
                    env.ref("payment.payment_method_kasikorn_bank").id,
                    env.ref("payment.payment_method_rabbit_line_pay").id,
                    env.ref("payment.payment_method_truemoney").id,
                    env.ref("payment.payment_method_fpx").id,
                    env.ref("payment.payment_method_fps").id,
                    env.ref("payment.payment_method_hd").id,
                    env.ref("payment.payment_method_maybank").id,
                    env.ref("payment.payment_method_pay_id").id,
                    env.ref("payment.payment_method_promptpay").id,
                    env.ref("payment.payment_method_techcom").id,
                    env.ref("payment.payment_method_tienphong").id,
                    env.ref("payment.payment_method_ttb").id,
                    env.ref("payment.payment_method_upi").id,
                    env.ref("payment.payment_method_vietcom").id,
                    env.ref("payment.payment_method_tendopay").id,
                    env.ref("payment.payment_method_alipay_hk").id,
                    env.ref("payment.payment_method_bharatqr").id,
                    env.ref("payment.payment_method_momo").id,
                    env.ref("payment.payment_method_octopus").id,
                    env.ref("payment.payment_method_maya").id,
                    env.ref("payment.payment_method_uatp").id,
                    env.ref("payment.payment_method_tenpay").id,
                    env.ref("payment.payment_method_enets").id,
                    env.ref("payment.payment_method_jkopay").id,
                    env.ref("payment.payment_method_payme").id,
                    env.ref("payment.payment_method_tmb").id,
                ]
            )
        ],
        "payment.payment_provider_authorize": [
            Command.set(
                [
                    env.ref("payment.payment_method_ach_direct_debit").id,
                    env.ref("payment.payment_method_card").id,
                ]
            )
        ],
        "payment.payment_provider_buckaroo": [
            Command.set(
                [
                    env.ref("payment.payment_method_bancontact").id,
                    env.ref("payment.payment_method_bank_reference").id,
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_ideal").id,
                    env.ref("payment.payment_method_afterpay_riverty").id,
                    env.ref("payment.payment_method_sepa_direct_debit").id,
                    env.ref("payment.payment_method_alipay").id,
                    env.ref("payment.payment_method_wechat_pay").id,
                    env.ref("payment.payment_method_klarna").id,
                    env.ref("payment.payment_method_trustly").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_in3").id,
                    env.ref("payment.payment_method_tinka").id,
                    env.ref("payment.payment_method_billink").id,
                    env.ref("payment.payment_method_kbc_cbc").id,
                    env.ref("payment.payment_method_belfius").id,
                    env.ref("payment.payment_method_giropay").id,
                    env.ref("payment.payment_method_p24").id,
                    env.ref("payment.payment_method_poste_pay").id,
                    env.ref("payment.payment_method_eps").id,
                    env.ref("payment.payment_method_cartes_bancaires").id,
                ]
            )
        ],
        # This one should be handled in payment_demo migration scripts
        # "payment.payment_provider_demo":
        #     [Command.set([
        #     env.ref('payment_demo.payment_method_demo').id,
        # ])],
        "payment.payment_provider_flutterwave": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_mpesa").id,
                    env.ref("payment.payment_method_mobile_money").id,
                    env.ref("payment.payment_method_bank_transfer").id,
                    env.ref("payment.payment_method_bank_account").id,
                    env.ref("payment.payment_method_credit").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_ussd").id,
                ]
            )
        ],
        "payment.payment_provider_mercado_pago": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_bank_transfer").id,
                    env.ref("payment.payment_method_paypal").id,
                ]
            )
        ],
        "payment.payment_provider_mollie": [
            Command.set(
                [
                    env.ref("payment.payment_method_bancontact").id,
                    env.ref("payment.payment_method_bank_transfer").id,
                    env.ref("payment.payment_method_belfius").id,
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_eps").id,
                    env.ref("payment.payment_method_giropay").id,
                    env.ref("payment.payment_method_ideal").id,
                    env.ref("payment.payment_method_kbc_cbc").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_paysafecard").id,
                    env.ref("payment.payment_method_p24").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_twint").id,
                ]
            )
        ],
        "payment_ogone.payment_provider_ogone": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_bancontact").id,
                    env.ref("payment.payment_method_belfius").id,
                    env.ref("payment.payment_method_bizum").id,
                    env.ref("payment.payment_method_klarna_paynow").id,
                    env.ref("payment.payment_method_klarna_pay_over_time").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_twint").id,
                    env.ref("payment.payment_method_axis").id,
                    env.ref("payment.payment_method_eps").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_paylib").id,
                    env.ref("payment.payment_method_p24").id,
                ]
            )
        ],
        "payment.payment_provider_paypal": [
            Command.set(
                [
                    env.ref("payment.payment_method_paypal").id,
                ]
            )
        ],
        "payment_payulatam.payment_provider_payulatam": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_pix").id,
                    env.ref("payment.payment_method_bank_reference").id,
                    env.ref("payment.payment_method_bank_transfer").id,
                    env.ref("payment.payment_method_pse").id,
                ]
            )
        ],
        "payment_payumoney.payment_provider_payumoney": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_netbanking").id,
                    env.ref("payment.payment_method_emi").id,
                    env.ref("payment.payment_method_upi").id,
                ]
            )
        ],
        "payment.payment_provider_razorpay": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_netbanking").id,
                    env.ref("payment.payment_method_upi").id,
                    env.ref("payment.payment_method_wallets_india").id,
                ]
            )
        ],
        "payment.payment_provider_sepa_direct_debit": [
            Command.set(
                [
                    env.ref("payment.payment_method_sepa_direct_debit").id,
                ]
            )
        ],
        "payment.payment_provider_sips": [
            Command.set(
                [
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_ideal").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_giropay").id,
                    env.ref("payment.payment_method_kbc_cbc").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_samsung_pay").id,
                    env.ref("payment.payment_method_bancontact").id,
                    env.ref("payment.payment_method_lyfpay").id,
                    env.ref("payment.payment_method_lydia").id,
                    env.ref("payment.payment_method_floa_bank").id,
                    env.ref("payment.payment_method_cofidis").id,
                    env.ref("payment.payment_method_frafinance").id,
                ]
            )
        ],
        "payment.payment_provider_stripe": [
            Command.set(
                [
                    env.ref("payment.payment_method_ach_direct_debit").id,
                    env.ref("payment.payment_method_affirm").id,
                    env.ref("payment.payment_method_afterpay").id,
                    env.ref("payment.payment_method_alipay").id,
                    env.ref("payment.payment_method_bacs_direct_debit").id,
                    env.ref("payment.payment_method_bancontact").id,
                    env.ref("payment.payment_method_becs_direct_debit").id,
                    env.ref("payment.payment_method_boleto").id,
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_cash_app_pay").id,
                    env.ref("payment.payment_method_clearpay").id,
                    env.ref("payment.payment_method_eps").id,
                    env.ref("payment.payment_method_fpx").id,
                    env.ref("payment.payment_method_giropay").id,
                    env.ref("payment.payment_method_grabpay").id,
                    env.ref("payment.payment_method_ideal").id,
                    env.ref("payment.payment_method_klarna").id,
                    env.ref("payment.payment_method_mobile_pay").id,
                    env.ref("payment.payment_method_multibanco").id,
                    env.ref("payment.payment_method_p24").id,
                    env.ref("payment.payment_method_paynow").id,
                    env.ref("payment.payment_method_paypal").id,
                    env.ref("payment.payment_method_pix").id,
                    env.ref("payment.payment_method_promptpay").id,
                    env.ref("payment.payment_method_revolut_pay").id,
                    env.ref("payment.payment_method_sepa_direct_debit").id,
                    env.ref("payment.payment_method_sofort").id,
                    env.ref("payment.payment_method_upi").id,
                    env.ref("payment.payment_method_wechat_pay").id,
                    env.ref("payment.payment_method_zip").id,
                ]
            )
        ],
        # This one should be handled in payment_custom migration scripts
        # "payment.payment_provider_transfer":
        #     [Command.set([
        #     env.ref('payment_custom.payment_method_wire_transfer').id,
        # ])],
        "payment.payment_provider_xendit": [
            Command.set(
                [
                    env.ref("payment.payment_method_7eleven").id,
                    env.ref("payment.payment_method_akulaku").id,
                    env.ref("payment.payment_method_bank_bca").id,
                    env.ref("payment.payment_method_bank_permata").id,
                    env.ref("payment.payment_method_billease").id,
                    env.ref("payment.payment_method_bni").id,
                    env.ref("payment.payment_method_bri").id,
                    env.ref("payment.payment_method_bsi").id,
                    env.ref("payment.payment_method_card").id,
                    env.ref("payment.payment_method_cashalo").id,
                    env.ref("payment.payment_method_cebuana").id,
                    env.ref("payment.payment_method_cimb_niaga").id,
                    env.ref("payment.payment_method_dana").id,
                    env.ref("payment.payment_method_gcash").id,
                    env.ref("payment.payment_method_grabpay").id,
                    env.ref("payment.payment_method_jeniuspay").id,
                    env.ref("payment.payment_method_kredivo").id,
                    env.ref("payment.payment_method_linkaja").id,
                    env.ref("payment.payment_method_mandiri").id,
                    env.ref("payment.payment_method_maya").id,
                    env.ref("payment.payment_method_ovo").id,
                    env.ref("payment.payment_method_qris").id,
                    env.ref("payment.payment_method_shopeepay").id,
                ]
            )
        ],
    }


def _get_provider_module_id(env):
    return {
        env.ref("base.module_payment_adyen").id: "payment.payment_provider_adyen",
        env.ref("base.module_payment_aps").id: "payment.payment_provider_aps",
        env.ref("base.module_payment_asiapay").id: "payment.payment_provider_asiapay",
        env.ref(
            "base.module_payment_authorize"
        ).id: "payment.payment_provider_authorize",
        env.ref("base.module_payment_buckaroo").id: "payment.payment_provider_buckaroo",
        # This one should be handled in payment_demo OpenUpgrade script
        # env.ref("base.module_payment_demo").id: "payment.payment_provider_demo",
        env.ref(
            "base.module_payment_flutterwave"
        ).id: "payment.payment_provider_flutterwave",
        env.ref(
            "base.module_payment_mercado_pago"
        ).id: "payment.payment_provider_mercado_pago",
        env.ref("base.module_payment_mollie").id: "payment.payment_provider_mollie",
        env.ref("base.module_payment_paypal").id: "payment.payment_provider_paypal",
        env.ref("base.module_payment_razorpay").id: "payment.payment_provider_razorpay",
        env.ref(
            "base.module_payment_sepa_direct_debit"
        ).id: "payment.payment_provider_sepa_direct_debit",
        env.ref("base.module_payment_sips").id: "payment.payment_provider_sips",
        env.ref("base.module_payment_stripe").id: "payment.payment_provider_stripe",
        # This one should be handled in payment_custom OpenUpgrade script
        # env.ref("base.module_payment_custom").id: "payment.payment_provider_transfer",
        env.ref("base.module_payment_xendit").id: "payment.payment_provider_xendit",
        env.ref(
            "base.module_payment_alipay"
        ).id: "payment_alipay.payment_provider_alipay",
        env.ref("base.module_payment_ogone").id: "payment_ogone.payment_provider_ogone",
        env.ref(
            "base.module_payment_payulatam"
        ).id: "payment_payulatam.payment_provider_payulatam",
        env.ref(
            "base.module_payment_payumoney"
        ).id: "payment_payumoney.payment_provider_payumoney",
    }


def _fill_provider_payment_method(env):
    providers = env["payment.provider"].search([])
    external_ids = providers.get_external_id()
    _PROVIDER_MODULE_MAPPING = _get_provider_module_id(env)
    _PROVIDER_PAYMENT_METHOD = _get_provider_payment_method(env)
    for provider in providers:
        provider_xml_id = False
        if external_ids.get(provider.id, False) in _PROVIDER_PAYMENT_METHOD.keys():
            provider_xml_id = external_ids.get(provider.id, False)
        elif provider.code:
            provider_xml_id = _PROVIDER_CODE_MAPPING.get(provider.code, False)
        elif provider.module_id:
            provider_xml_id = _PROVIDER_MODULE_MAPPING.get(provider.module_id.id)

        if provider_xml_id:
            provider.write(
                {
                    "payment_method_ids": _PROVIDER_PAYMENT_METHOD.get(
                        provider_xml_id, False
                    )
                }
            )


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
    _fill_provider_payment_method(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, ["payment.payment_transaction_user_rule"]
    )
    _fill_payment_method(env)
