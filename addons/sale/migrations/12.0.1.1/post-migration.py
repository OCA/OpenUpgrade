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


def fill_sale_order_line_is_expense(cr):
    # fill is_expense
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_line sol
        SET is_expense = TRUE
        FROM account_analytic_line aal
        JOIN product_product pp ON aal.product_id = pp.id
        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE aal.so_line = sol.id AND aal.amount <= 0
            AND pt.expense_policy IS NOT NULL AND pt.expense_policy != 'no'
        """
    )


def fill_sale_order_line_qty_delivered_method(cr):
    # set qty_delivered_method = 'analytic'
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_line sol
        SET qty_delivered_method = 'analytic'
        WHERE is_expense"""
    )
    if openupgrade.column_exists(cr, 'sale_order', 'warehouse_id'):
        # sale_stock is installed
        # set qty_delivered_method = 'stock_move'
        openupgrade.logged_query(
            cr, """
            UPDATE sale_order_line sol
            SET qty_delivered_method = 'stock_move'
            FROM product_product pp
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE sol.product_id = pp.id AND NOT sol.is_expense
                AND pt.type IN ('consu', 'product')
            """
        )
    # set qty_delivered_method = 'timesheet'
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_line sol
        SET qty_delivered_method = 'timesheet'
        FROM product_product pp
        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE sol.product_id = pp.id AND NOT sol.is_expense
            AND pt.type = 'service' AND pt.service_type = 'timesheet'
        """
    )
    # set qty_delivered_method = 'manual'
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order_line sol
        SET qty_delivered_method = 'manual'
        WHERE qty_delivered_method IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    type_change_payment_transaction_and_sale_order(env)
    fill_sale_order_line_is_expense(env.cr)
    fill_sale_order_line_qty_delivered_method(env.cr)
    openupgrade.load_data(
        env.cr, 'sale', 'migrations/12.0.1.1/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'sale', [
            'email_template_edi_sale',
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'sale.mail_template_data_notification_email_sale_order',
        ],
    )
