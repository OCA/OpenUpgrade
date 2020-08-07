# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2016 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from pprint import pformat

from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


def set_invoice_policy(env):
    value = env['ir.values'].get_default('sale.order', 'order_policy')
    policy = 'delivery' if value == 'picking' else 'order'
    env['ir.values'].set_default('product.template', 'invoice_policy', policy)
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_template
        SET invoice_policy = %s
        WHERE invoice_policy IS NULL AND type != 'service';""",
        (policy,))
    openupgrade.logged_query(
        env.cr,
        """UPDATE product_template
        SET invoice_policy = 'order'
        WHERE invoice_policy IS NULL""")


def set_track_service(cr):
    """ Set all records to manual """
    openupgrade.logged_query(cr, """
        UPDATE product_template
        SET track_service = 'manual'
        WHERE track_service IS NULL;
    """)


def set_dummy_product(env):
    product = env['product.product'].create({
        'name': 'Any product',
        'type': 'service',
        'order_policy': 'manual',
    })
    env.cr.execute(
        """UPDATE sale_order_line
        SET product_id = %s WHERE product_id IS NULL""",
        (product.id,))


def set_crm_team_message_types(env):
    """ Add two new default message types to existing subscriptions """
    env['mail.followers'].search([('res_model', '=', 'crm.team')]).write(
        {'subtype_ids': [
            (4, env.ref('sale.mt_salesteam_invoice_confirmed').id),
            (4, env.ref('sale.mt_salesteam_invoice_created').id)]})


@openupgrade.logging()
def set_so_line_amounts(env):
    """We replicate here the code of the compute function and set the values
    finally via SQL for avoiding the trigger of the rest of the computed
    fields that depends on these fields.
    """
    lines = env['sale.order.line'].search([])
    for line in lines:
        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        taxes = line.tax_id.compute_all(
            price, line.order_id.currency_id, line.product_uom_qty,
            product=line.product_id, partner=line.order_id.partner_id)
        env.cr.execute("""
            UPDATE sale_order_line
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


def set_so_line_computed_rest(env):
    """Emulate the computation of the rest of the computed fields through
    equivalente SQL querys.

    Note: qty_to_invoice is set in the deferred script after qty_delivered
    is set in sale_stock and sale_mrp
    """
    uom_precision = env['decimal.precision'].precision_get('Product Unit of Measure')
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line
        SET price_reduce = CASE
            -- ROUND() missing in original code, but it's a bug
            WHEN ROUND(product_uom_qty, %(uom_precision)s) != 0
                THEN price_subtotal / product_uom_qty
            ELSE 0.0
        END""",
        {"uom_precision": uom_precision})
    # Fail if there are UoM mismatches
    openupgrade.logged_query(
        env.cr,
        """
            SELECT
                rel.order_line_id,
                sol_u.id AS order_line_uom_id,
                sol_u.category_id AS order_line_uom_category_id,
                sol.product_id AS order_line_product_id,
                rel.invoice_line_id,
                ail_u.id AS invoice_line_uom_id,
                ail_u.category_id AS invoice_line_uom_category_id,
                ail_pp.id AS invoice_line_product_id,
                ail_pt.name AS invoice_line_product_template_name
            FROM sale_order_line_invoice_rel rel
                JOIN sale_order_line sol ON
                    rel.order_line_id = sol.id
                JOIN account_invoice_line ail ON
                    rel.invoice_line_id = ail.id
                JOIN product_product ail_pp ON ail_pp.id = ail.product_id
                JOIN product_template ail_pt ON ail_pt.id = ail_pp.product_tmpl_id
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN product_uom ail_u on (ail_u.id = ail.uom_id)
                JOIN product_uom sol_u on (sol_u.id = sol.product_uom)
            WHERE
                ail_u.category_id != sol_u.category_id
        """
    )
    uom_category_mismatches = env.cr.dictfetchall()
    if uom_category_mismatches:
        raise Exception(
            "Found these mismatching UoM in related sale.order.line "
            "and account.invoice.line records: %s" %
            pformat(uom_category_mismatches))
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET qty_invoiced = sub.qty
        FROM (
            SELECT rel.order_line_id,
                SUM(CASE
                    WHEN ai.type = 'out_invoice'
                        THEN ail.quantity / u.factor * u2.factor
                    WHEN ai.type = 'out_refund'
                        THEN -ail.quantity / u.factor * u2.factor
                    ELSE 0.0
                END) AS qty
            FROM sale_order_line_invoice_rel rel
                JOIN sale_order_line sol2 ON
                    rel.order_line_id = sol2.id
                JOIN account_invoice_line ail ON
                    rel.invoice_line_id = ail.id
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN product_uom u on (u.id = ail.uom_id)
                JOIN product_uom u2 on (u2.id = sol2.product_uom)
            WHERE ai.state != 'cancel'
            GROUP BY rel.order_line_id
        ) AS sub
        WHERE sol.id = sub.order_line_id""")
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET currency_id = pp.currency_id
        FROM sale_order so
        JOIN product_pricelist pp ON pp.id = so.pricelist_id
        WHERE so.id = sol.order_id""")


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    set_dummy_product(env)
    set_invoice_policy(env)
    set_track_service(cr)
    set_crm_team_message_types(env)
    set_so_line_amounts(env)
    set_so_line_computed_rest(env)
    openupgrade.load_data(
        cr, 'sale', 'migrations/9.0.1.0/noupdate_changes.xml')
