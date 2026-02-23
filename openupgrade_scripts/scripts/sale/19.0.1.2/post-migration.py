# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def res_company_downpayment_account_id(env):
    """
    Set res_company#downpayment_account_id from categories or default
    """

    def get_default(company):
        env.cr.execute(
            """
            SELECT json_value
            FROM ir_default
            JOIN ir_model_fields
            ON ir_default.field_id=ir_model_fields.id
            JOIN ir_model
            ON ir_model_fields.model_id=ir_model.id
            WHERE
            ir_model.model='product.category' AND
            ir_model_fields.name='property_account_downpayment_categ_id'
            AND """
            + ("company_id IS NULL" if not company else f"company_id={company.id}")
        )
        result = env.cr.fetchone()
        return result and int(result[0]) or None

    global_default = get_default(None)

    for company in env["res.company"].search([]):
        company_default = get_default(company)

        env.cr.execute(
            f"""
            SELECT account_id FROM (
                SELECT
                property_account_downpayment_categ_id->'{company.id}' account_id,
                COUNT(id) cnt
                FROM product_category
                GROUP BY property_account_downpayment_categ_id->'{company.id}'
            ) account_counts
            ORDER BY cnt DESC
            LIMIT 1
            """
        )
        account_id = env.cr.fetchone()[0]

        if not account_id:
            account_id = company_default or global_default

        if account_id:
            company.downpayment_account_id = account_id


def action_orders(env):
    """
    This action had its domain deleted
    """
    env.ref("sale.action_orders").domain = False


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "sale", "19.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "sale",
        [
            "email_template_edi_sale",
            "mail_template_sale_confirmation",
            "mail_template_sale_payment_executed",
        ],
        ["body_html"],
    )
    res_company_downpayment_account_id(env)
    action_orders(env)
