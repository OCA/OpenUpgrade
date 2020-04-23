# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def type_change_payment_transaction_and_sale_order(env):
    if openupgrade.column_exists(
            env.cr, 'payment_transaction',
            openupgrade.get_legacy_name('sale_order_id')):
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
            WHERE sol.product_id = pp.id AND sol.is_expense IS NOT TRUE
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
        WHERE sol.product_id = pp.id AND sol.is_expense IS NOT TRUE
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


def fill_sale_order_line_untaxed_amount_invoiced(env):
    """Fill by SQL this computed stored field when possible, because it's
    very slow by ORM.
    """
    # Code that mimicks by SQL: https://github.com/OCA/OpenUpgrade/blob/27d82a/addons/sale/models/sale.py#L1333-L1351
    openupgrade.logged_query(
        env.cr,
        """UPDATE sale_order_line sol
        SET untaxed_amount_invoiced = sub.amount
        FROM (
            SELECT rel.order_line_id,
                SUM(CASE
                    WHEN ai.type = 'out_invoice' THEN ail.price_subtotal
                    WHEN ai.type = 'out_refund' THEN -ail.price_subtotal
                END) AS amount
            FROM sale_order_line_invoice_rel rel
                JOIN account_invoice_line ail ON rel.invoice_line_id = ail.id
                JOIN account_invoice ai ON ai.id = ail.invoice_id
            WHERE ai.state IN ('open', 'in_payment', 'paid')
            GROUP BY rel.order_line_id
        ) AS sub
        WHERE sol.id = sub.order_line_id""")
    # Now recompute by ORM those with different currency
    env.cr.execute(
        """SELECT DISTINCT(sol.id)
        FROM sale_order_line_invoice_rel rel
            JOIN account_invoice_line ail ON rel.invoice_line_id = ail.id
            JOIN sale_order_line sol ON rel.order_line_id = sol.id
        WHERE sol.currency_id != ail.currency_id""")
    env['sale.order.line'].browse(
        [x[0] for x in env.cr.fetchall()])._compute_untaxed_amount_invoiced()


def fill_sale_order_line_untaxed_amount_to_invoice(env):
    """Fill by SQL this computed stored field because it's very slow by ORM."""
    # Code that mimicks by SQL: https://github.com/OCA/OpenUpgrade/blob/27d82a/addons/sale/models/sale.py#L1354-L1377
    openupgrade.logged_query(
        env.cr,
        """UPDATE sale_order_line sol
        SET untaxed_amount_to_invoice = sub.amount
        FROM (
            SELECT sol2.id AS id,
                (
                    CASE WHEN sol2.state IN ('sale', 'done') THEN (
                        CASE WHEN pt.invoice_policy = 'delivery' THEN
                            sol2.price_reduce * sol2.qty_delivered -
                            sol2.untaxed_amount_invoiced
                        ELSE
                            sol2.price_reduce * sol2.product_uom_qty -
                            sol2.untaxed_amount_invoiced
                        END
                    )
                    ELSE 0.0
                    END
                ) AS amount
            FROM sale_order_line sol2
            JOIN product_product pp ON pp.id = sol2.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
        ) AS sub
        WHERE sub.id = sol.id
        """)


def set_group_sale_order_dates(cr):
    cr.execute(
        """SELECT res_id FROM ir_model_data WHERE module = 'base'
        AND model = 'res.groups' AND name = 'group_user'""")
    user_group_id = cr.fetchone()[0]
    cr.execute(
        """SELECT res_id FROM ir_model_data WHERE module = 'sale'
        AND model = 'res.groups' AND name = 'group_sale_order_dates'""")
    sale_order_dates_group_id = cr.fetchone()[0]
    cr.execute(
        """
        INSERT INTO res_groups_implied_rel (gid, hid)
        VALUES (%s, %s)
    """, (user_group_id, sale_order_dates_group_id),
    )


def fill_res_company_portal_confirmation(cr):
    if openupgrade.column_exists(
            cr, 'sale_order',
            openupgrade.get_legacy_name('payment_tx_id')):
        openupgrade.logged_query(
            cr, """
            UPDATE res_company
            SET portal_confirmation_pay = TRUE
            """
        )
    cr.execute(
        """SELECT value FROM ir_config_parameter
        WHERE key = 'sale.sale_portal_confirmation_options'""")
    value = cr.fetchone()
    if value and value[0] == 'sign':
        openupgrade.logged_query(
            cr, """
            UPDATE res_company
            SET portal_confirmation_sign = TRUE"""
        )


@openupgrade.migrate()
def migrate(env, version):
    type_change_payment_transaction_and_sale_order(env)
    fill_res_company_portal_confirmation(env.cr)
    fill_sale_order_line_is_expense(env.cr)
    fill_sale_order_line_qty_delivered_method(env.cr)
    fill_sale_order_line_untaxed_amount_invoiced(env)
    fill_sale_order_line_untaxed_amount_to_invoice(env)
    if openupgrade.column_exists(
            env.cr, 'sale_order',
            openupgrade.get_legacy_name('commitment_date')):
        set_group_sale_order_dates(env.cr)
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
