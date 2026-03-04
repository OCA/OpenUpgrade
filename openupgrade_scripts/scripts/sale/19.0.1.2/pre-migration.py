# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_added_fields = [
    (
        "collapse_composition",
        "sale.order.line",
        "sale_order_line",
        "boolean",
        None,
        "sale",
        False,
    ),
    (
        "collapse_prices",
        "sale.order.line",
        "sale_order_line",
        "boolean",
        None,
        "sale",
        False,
    ),
]


_renamed_fields = [
    (
        "sale.order.line",
        "sale_order_line",
        "product_uom",
        "product_uom_id",
    ),
    (
        "sale.order.line",
        "sale_order_line",
        "tax_id",
        "tax_ids",
    ),
]

_renamed_xmlids = [
    ("sale_async_emails.async_emails", "sale.async_emails"),
    ("sale_async_emails.cron", "sale.send_pending_emails_cron"),
]

_deleted_xmlids = [
    "sale.sale_order_cancel_rule",
    "sale.sale_payment_provider_onboarding_wizard_rule",
    "sale.mail_template_sale_cancellation",
    "sale.mail_act_sale_upsell",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _added_fields)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.rename_xmlids(env.cr, _renamed_xmlids)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
