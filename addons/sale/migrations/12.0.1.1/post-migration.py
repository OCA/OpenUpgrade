# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def type_change_payment_transaction_and_sale_order(env):
    if openupgrade.column_exists(
            env.cr, 'sale.order',
            openupgrade.get_legacy_name('payment_tx_id')):
        openupgrade.m2o_to_x2m(
            env.cr,
            env['sale.order'], 'sale_order',
            'transaction_ids', openupgrade.get_legacy_name('payment_tx_id')
        )
        openupgrade.m2o_to_x2m(
            env.cr,
            env['payment.transaction'], 'payment_transaction',
            'sale_order_ids', openupgrade.get_legacy_name('sale_order_id')
        )


def recompute_sale_order_line_invoicing(env):
    sale_lines = env['sale.order.line'].search([])
    sale_lines._compute_untaxed_amount_invoiced()
    sale_lines._compute_untaxed_amount_to_invoice()


@openupgrade.migrate()
def migrate(env, version):
    type_change_payment_transaction_and_sale_order(env)
    recompute_sale_order_line_invoicing(env)
    openupgrade.load_data(
        env.cr, 'sale', 'migrations/12.0.1.1/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'sale.mail_template_data_notification_email_sale_order',
        ],
    )
