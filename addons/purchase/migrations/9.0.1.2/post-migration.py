# -*- coding: utf-8 -*-
# Copyright 2015 Eficent Business and IT Consulting Services S.L.
# Copyright 2015 Serpent Consulting Services Pvt. Ltd.
# Copyright 2019 Tecnativa - Jairo Llopis
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from pprint import pformat

from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


def set_dummy_product(env):
    products = env['product.product'].search([('name', '=', 'Any product')])
    if not products:
        product = env['product.product'].create({
            'name': 'Any product',
            'type': 'service',
            'order_policy': 'manual',
        })
    else:
        product = products[0]

    env.cr.execute(
        """UPDATE purchase_order_line
        SET product_id = %s WHERE product_id IS NULL""",
        (product.id,))


def pricelist_property(cr, env):
    # Created res.currency properties from Purchase Pricelist
    property_rec = env['ir.property'].search(
        [('name', '=', 'property_product_pricelist_purchase'),
         '|',
         ('res_id', 'like', 'res.partner%'),
         ('res_id', '=', False)]
    )
    pricelist = []
    partner = []
    currency = []
    for prop in property_rec:
        if prop.value_reference:
            product_pricelist = prop.value_reference
            res_partner = prop.res_id
            pricelist_id = product_pricelist.split(',')[1]
            pricelist_id = int(pricelist_id)
            currency_rec = env['product.pricelist'].\
                search_read([('id', 'in', [pricelist_id])], ['currency_id'])
            if not currency_rec:
                # Some DB may have incorrect pricelist ids in this
                # property.  It seems that some old bug left ir.properties
                # when pricelists where deleted.
                continue
            currency.append(currency_rec[0]['currency_id'][0])
            pricelist.append(pricelist_id)
            if res_partner:
                partner_id = res_partner.split(',')[1]
                partner_id = int(partner_id)
                partner.append(partner_id)
                cr.execute("""
                insert into ir_property (name, type, company_id, fields_id,
                value_reference, res_id)
                values ('property_purchase_currency_id', 'many2one', 1,
                (select id from ir_model_fields where model = 'res.partner'
                and name = 'property_purchase_currency_id'),
                'res.currency,%(currency)s', 'res.partner,%(partner)s')
                """ % {'currency': currency[-1], 'partner': partner[-1]})
            else:
                cr.execute("""
                insert into ir_property (name, type, company_id, fields_id,
                value_reference)
                values ('property_purchase_currency_id', 'many2one', 1,
                (select id from ir_model_fields where model = 'res.partner'
                and name = 'property_purchase_currency_id'),
                 'res.currency,%(currency)s')
                """ % {'currency': currency[-1]})


def account_properties(cr):
    # Handle account properties as their names are changed.
    cr.execute("""
            update ir_property set name = 'property_account_payable_id',
            fields_id = (select id from ir_model_fields where model
            = 'res.partner' and name = 'property_account_payable_id')
            where name = 'property_account_payable' and (res_id like
            'res.partner%' or res_id is null)
            """)
    cr.execute("""
            update ir_property set fields_id = (select id from
            ir_model_fields where model = 'res.partner' and
            name = 'property_account_receivable_id'), name =
            'property_account_receivable_id' where
            name = 'property_account_receivable' and (res_id like
            'res.partner%' or res_id is null)
            """)


@openupgrade.logging()
def set_po_line_amounts(env):
    """We replicate here the code of the compute function and set the values
    finally via SQL for avoiding the trigger of the rest of the computed
    fields that depends on these fields.

    Replaces code from https://bit.ly/2rgpTTV
    """
    lines = env['purchase.order.line'].search([])
    for line in lines:
        taxes = line.taxes_id.compute_all(
            line.price_unit, line.order_id.currency_id, line.product_qty,
            product=line.product_id, partner=line.order_id.partner_id)
        env.cr.execute("""
            UPDATE purchase_order_line
            SET price_tax = %s,
                price_total = %s,
                price_subtotal = %s
            WHERE id = %s""", (
                taxes['total_included'] - taxes['total_excluded'],
                taxes['total_included'],
                taxes['total_excluded'],
                line.id,
            )
        )


@openupgrade.logging()
def set_po_line_computed_rest(env):
    """Emulate the computation of the rest of the computed fields through
    equivalent SQL queries.
    """
    uom_precision = env['decimal.precision'].precision_get('Product Unit of Measure')
    # Fail if there are UoM mismatches
    # Replace https://github.com/OCA/OpenUpgrade/blob/195b61a948dff1c64279eb68f0544/addons/product/product.py#L120-L122
    env.cr.execute(
        """
            SELECT
                pol.id AS order_line_id,
                pol_u.id AS order_line_uom_id,
                pol_u.category_id AS order_line_uom_category_id,
                pol.product_id AS order_line_product_id,
                ail.id AS invoice_line_id,
                ail_u.id AS invoice_line_uom_id,
                ail_u.category_id AS invoice_line_uom_category_id,
                ail_pp.id AS invoice_line_product_id,
                ail_pt.name AS invoice_line_product_template_name
            FROM purchase_order_line pol
                JOIN account_invoice_line ail ON
                    pol.id = ail.purchase_line_id
                JOIN product_product ail_pp ON ail_pp.id = ail.product_id
                JOIN product_template ail_pt ON ail_pt.id = ail_pp.product_tmpl_id
                JOIN product_uom ail_u on (ail_u.id = ail.uom_id)
                JOIN product_uom pol_u on (pol_u.id = pol.product_uom)
            WHERE
                ail_u.category_id != pol_u.category_id
        """
    )
    uom_category_mismatches = env.cr.dictfetchall()
    if uom_category_mismatches:
        raise Exception(
            "Found these mismatching UoM in related purchase.order.line "
            "and account.invoice.line records: %s" %
            pformat(uom_category_mismatches))
    # Replace https://github.com/OCA/OpenUpgrade/blob/195b61a948dff1c64279eb68f05/addons/purchase/purchase.py#L477-L487
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE purchase_order_line pol
            SET qty_invoiced = sub.qty
            FROM (
                SELECT
                    pol2.id,
                    SUM(
                        ail.quantity / pol2_u.factor * ail_u.factor * (
                            CASE
                                WHEN ai.type = 'in_invoice' THEN 1
                                ELSE -1
                            END
                        )
                    ) AS qty
                FROM purchase_order_line pol2
                    JOIN account_invoice_line ail ON pol2.id = ail.purchase_line_id
                    JOIN account_invoice ai ON ai.id = ail.invoice_id
                    JOIN product_uom pol2_u ON pol2_u.id = ail.uom_id
                    JOIN product_uom ail_u ON ail_u.id = pol2.product_uom
                WHERE
                    ai.state != 'cancel' AND
                    ai.type IN ('in_invoice', 'in_refund')
                GROUP BY pol2.id
            ) AS sub
            WHERE pol.id = sub.id
        """
    )
    env.cr.execute("""
        SELECT
            pol.id AS order_line_id,
            pol_u.id AS order_line_uom_id,
            pol_u.category_id AS order_line_uom_category_id,
            pol.product_id AS order_line_product_id,
            sm.id AS stock_move_id,
            sm_u.id AS stock_move_uom_id,
            sm_u.category_id AS stock_move_uom_category_id,
            sm_pp.id AS stock_move_product_id,
            sm_pt.name AS stock_move_product_template_name
        FROM purchase_order_line pol
            JOIN stock_move sm ON pol.id = sm.purchase_line_id
            JOIN product_product sm_pp ON sm_pp.id = sm.product_id
            JOIN product_template sm_pt ON sm_pt.id = sm_pp.product_tmpl_id
            JOIN product_uom sm_u on (sm_u.id = sm.product_uom)
            JOIN product_uom pol_u on (pol_u.id = pol.product_uom)
        WHERE
            sm_u.category_id != pol_u.category_id""")
    uom_category_mismatches = env.cr.dictfetchall()
    if uom_category_mismatches:
        raise Exception(
            "Found these mismatching UoM in related purchase.order.line "
            "and stock.move records: %s" % pformat(uom_category_mismatches))
    # Replace https://github.com/OCA/OpenUpgrade/blob/195b61a948dff1c64279eb68f05/addons/purchase/purchase.py#L492-L498
    # and leave the rest of the method to be called in end-migration, where mrp module will be available for
    # sure in the environment if it is installed
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET qty_received = sub.qty_received
        FROM (
            SELECT CASE
                WHEN MIN(po.state) NOT IN ('purchase', 'done') THEN 0.0
                WHEN MIN(po.state) IN ('purchase', 'done')
                    AND MIN(pt.type) NOT IN ('consu', 'product')
                    THEN MIN(pol2.product_qty)
                ELSE SUM(CASE
                    WHEN sm.state IS NULL OR sm.state != 'done' THEN 0.0
                    ELSE COALESCE(sm.product_uom_qty / u.factor * u2.factor, 0)
                    END)
                END
            AS qty_received,
                sm.purchase_line_id AS id
            FROM purchase_order_line pol2
            JOIN purchase_order po ON pol2.order_id = po.id
            JOIN product_product pp ON pol2.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN stock_move sm ON sm.purchase_line_id = pol2.id
            LEFT JOIN product_uom u on (u.id = sm.product_uom)
            LEFT JOIN product_uom u2 on (u2.id = pol2.product_uom)
            GROUP BY sm.purchase_line_id
        ) sub
        WHERE sub.id = pol.id""",
    )
    # Replace https://github.com/OCA/OpenUpgrade/blob/195b61a948dff1c64279eb68f0544/addons/purchase/purchase.py#L47-L60
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE purchase_order po
            SET invoice_status = CASE
                WHEN po.state != 'purchase' THEN 'no'
                WHEN sub.lines_to_invoice > 0 THEN 'to invoice'
                WHEN sub.lines = sub.lines_invoiced THEN 'invoiced'
                ELSE 'no'
            END
            FROM (
                SELECT
                    po2.id,
                    COUNT(pol1.*) AS lines,
                    COUNT(pol2.*) AS lines_to_invoice,
                    COUNT(pol3.*) AS lines_invoiced
                FROM
                    purchase_order po2
                    -- pol1 contains all lines
                    LEFT JOIN purchase_order_line pol1
                        ON po2.id = pol1.order_id
                    -- pol2 contains lines to invoice
                    LEFT JOIN purchase_order_line pol2
                        ON po2.id = pol2.order_id AND
                        ROUND(pol2.qty_invoiced::numeric, %(uom_precision)s) <
                        ROUND(pol2.product_qty, %(uom_precision)s)
                    -- pol3 contains invoiced lines
                    LEFT JOIN purchase_order_line pol3
                        ON po2.id = pol3.order_id AND
                        ROUND(pol3.qty_invoiced::numeric, %(uom_precision)s) >=
                        ROUND(pol3.product_qty, %(uom_precision)s)
                GROUP BY po2.id
            ) AS sub
            WHERE po.id = sub.id
        """,
        {"uom_precision": uom_precision},
    )
    # Fill related column faster by SQL
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE purchase_order_line pol
            SET currency_id = po.currency_id
            FROM purchase_order po
            WHERE po.id = pol.order_id
        """,
    )


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    set_dummy_product(env)
    pricelist_property(cr, env)
    account_properties(cr)
    set_po_line_amounts(env)
    set_po_line_computed_rest(env)
