# Copyright 2023 Viindoo - Nguyễn Đại Dương
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _fill_aml_is_downpayment(env):
    """Set the value from the linked sale.order.line."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET is_downpayment = sol.is_downpayment
        FROM sale_order_line_invoice_rel rel
        JOIN sale_order_line sol ON sol.id = rel.order_line_id
        WHERE aml.id = rel.invoice_line_id
            AND sol.is_downpayment
        """,
    )


def try_delete_noupdate_records(env):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "sale.mail_notification_paynow_online",
            "sale.sale_payment_acquirer_onboarding_wizard_rule",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_aml_is_downpayment(env)
    openupgrade.load_data(env.cr, "sale", "16.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "sale", ["email_template_edi_sale", "mail_template_sale_confirmation"]
    )
    try_delete_noupdate_records(env)
