# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_account_move_team_partner_ids(cr):
    openupgrade.logged_query(
        cr, """
            UPDATE account_move am
            SET partner_shipping_id = ai.partner_shipping_id, team_id = ai.team_id
            FROM account_invoice ai
            WHERE am.old_invoice_id = ai.id
            """
    )


def update_sale_order_line_invoice_rel(cr):
    openupgrade.logged_query(
        cr, """
            UPDATE sale_order_line_invoice_rel solir
            SET invoice_line_id = aml.id
            FROM account_invoice_line ail
            JOIN account_move_line aml ON aml.old_invoice_line_id = ail.id
            WHERE solir.invoice_line_id = ail.id
            """
    )


def update_product_attribute_custom_value(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE product_attribute_custom_value pacv
        SET custom_product_template_attribute_value_id = ptav.id
        FROM product_attribute_value pav
        JOIN product_template_attribute_value ptav
            ON ptav.product_attribute_value_id = pav.id
        WHERE pacv.{} = pav.id
            AND pacv.custom_product_template_attribute_value_id IS NULL
        """.format(openupgrade.get_legacy_name('attribute_value_id'))
    )


@openupgrade.migrate()
def migrate(env, version):
    update_account_move_team_partner_ids(env.cr)
    update_sale_order_line_invoice_rel(env.cr)
    update_product_attribute_custom_value(env.cr)
    openupgrade.load_data(env.cr, 'sale', 'migrations/13.0.1.1/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'sale', [
            'email_template_edi_sale',
        ],
    )
