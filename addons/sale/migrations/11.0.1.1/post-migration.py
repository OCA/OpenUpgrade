# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('sale.group_display_incoterm', 'sale_stock.group_display_incoterm'),
]


def activate_proforma(env):
    """If module `sale_proforma_report` (OCA/sale-reporting) was installed we
    need to activate the "Pro-forma Invoices" setting as the module was
    deprecated in favour of it."""
    if openupgrade.column_exists(env.cr, 'sale_order', 'proforma'):
        employee_group = env.ref('base.module_category_human_resources')
        proforma_group = env.ref('sale.group_proforma_sales')
        employee_group.write({'implied_ids': [(4, proforma_group.id)]})


@openupgrade.logging()
def fill_sale_order_line_computed(env):
    """Compute through SQL sale.order.line fields for speeding up migration."""
    # We first set everything to 0 in both fields
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET amt_invoiced = 0.00,
            amt_to_invoice = 0.00
        """,
    )
    # Then we set the invoiced amount for the order lines with related invoice
    # lines and same currency
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET amt_invoiced = sub.amount
        FROM (
            SELECT rel.order_line_id,
                ail.currency_id,
                SUM(ail.price_total) AS amount
            FROM sale_order_line_invoice_rel rel
                INNER JOIN account_invoice_line ail ON
                    rel.invoice_line_id = ail.id
                INNER JOIN account_invoice ai ON ai.id = ail.invoice_id
            WHERE ai.state IN ('open', 'paid')
            GROUP BY rel.order_line_id,
                ail.currency_id
        ) AS sub
        WHERE sol.id = sub.order_line_id
            AND sol.currency_id = sub.currency_id
        """,
    )
    # Now we set the amt_to_invoice with this simplified computation, but
    # before discounting refunded invoiced. We apply a fixed rounding for
    # avoiding resolution problems. It also uses a trick using the same table
    # 2 times for avoiding to perform a subquery.
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET amt_to_invoice = ROUND(
            (CASE WHEN COALESCE(pt.invoice_policy, 'x') = 'delivery'
             THEN sol.price_reduce_taxinc * sol.qty_delivered
             ELSE sol.price_total END) - sol.amt_invoiced, 5
        )
        FROM sale_order_line sol2
        LEFT JOIN product_product pp ON pp.id = sol2.product_id
        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sol2.id = sol.id
            AND sol.state IN ('sale', 'done')
        """,
    )
    # We have to do this second query that reduces the invoiced amount due to
    # the refunded amount as the computation mixes several tables that can't
    # be combined together. The computation is not exact, as we reduce amount
    # for all lines with same product, but it's not even correct on upstream,
    # as there's no real link.
    # See https://github.com/odoo/odoo/pull/26054#pullrequestreview-143472733
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET amt_invoiced = sol.amt_invoiced - sub.amount
        FROM (
            SELECT sol.id,
                SUM(ail.price_total) AS amount
            FROM sale_order_line sol
                INNER JOIN sale_order_line_invoice_rel rel
                    ON sol.id = rel.order_line_id
                INNER JOIN account_invoice_line ail
                    ON rel.invoice_line_id = ail.id
                INNER JOIN account_invoice ai ON ai.id = ail.invoice_id
                INNER JOIN account_invoice ai2 ON ai2.refund_invoice_id = ai.id
            WHERE ai.state IN ('open', 'paid')
                AND ai2.state IN ('open', 'paid')
                AND ail.product_id = sol.product_id
            GROUP BY sol.id
        ) AS sub
        WHERE sol.id = sub.id""",
    )
    # Finally, launch an ORM computation of lines with different invoice
    # currency than sales order one
    env.cr.execute(
        """SELECT sol.id
        FROM sale_order_line sol
        INNER JOIN sale_order_line_invoice_rel rel
            ON rel.order_line_id = sol.id
        INNER JOIN account_invoice_line ail
            on ail.id = rel.invoice_line_id
        WHERE ail.currency_id != sol.currency_id
        """
    )
    so_lines = env['sale.order.line'].browse([
        x[0] for x in env.cr.fetchall()
    ])
    so_lines._compute_invoice_amount()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fill_sale_order_line_computed(env)
    openupgrade.load_data(
        env.cr, 'sale', 'migrations/11.0.1.1/noupdate_changes.xml',
    )
    openupgrade.delete_record_translations(
        env.cr, 'sale', [
            'email_template_edi_sale',
            'mail_template_data_notification_email_sale_order',
        ],
    )
    activate_proforma(env)
