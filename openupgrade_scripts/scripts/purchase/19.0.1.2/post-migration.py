# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def purchase_order_fields(env):
    """
    Set state = purchase for orders with state == 'done'
    Set locked = true for orders in state purchase if their company is configured
    accordingly
    Set acknowledged=True for orders in state purchase to avoid unexpected reminder
    mails
    """
    env.cr.execute("UPDATE purchase_order SET state='purchase' WHERE state='done'")
    env.cr.execute("UPDATE purchase_order SET acknowledged=True WHERE state='purchase'")
    env.cr.execute(
        """
        UPDATE purchase_order SET locked=TRUE
        FROM res_company
        WHERE
        purchase_order.company_id=res_company.id
        AND res_company.po_lock='lock'
        """
    )


def purchase_order_line_technical_price_unit(env):
    """
    Initialized technical_price_unit with price_unit
    """
    env.cr.execute("UPDATE purchase_order_line SET technical_price_unit=price_unit")


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "purchase", "19.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "purchase",
        [
            "email_template_edi_purchase",
            "email_template_edi_purchase_done",
            "email_template_edi_purchase_reminder",
        ],
        ["body_html"],
    )
    purchase_order_fields(env)
    purchase_order_line_technical_price_unit(env)
