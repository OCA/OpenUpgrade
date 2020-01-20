# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def move_fields_from_invoice_to_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET website_id = ai.website_id
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id""",
    )


def fill_website_sale_product_image(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE product_image
        SET name = 'random_name_' || id
        WHERE name IS NULL 
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    move_fields_from_invoice_to_moves(env)
    fill_website_sale_product_image(env)
    openupgrade.load_data(env.cr, "website_sale",
                          "migrations/13.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, 'website_sale', [
            'mail_template_sale_cart_recovery',
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "website_sale.payment_token_salesman_rule",
            "website_sale.payment_transaction_salesman_rule",
        ]
    )
