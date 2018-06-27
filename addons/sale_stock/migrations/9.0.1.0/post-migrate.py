# -*- coding: utf-8 -*-
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    set_sale_order_qty_delivered(env)
    if openupgrade.is_module_installed(env.cr, 'stock_account'):
        set_product_template_invoice_policy_delivery(env)
    set_incoterm_group(env)
    set_invoice_incoterms_id(env)


def set_incoterm_group(env):
    """ Set the new sale Incoterm configuration option if incoterms
    are used at all in this database. """

    env.cr.execute("SELECT incoterm FROM sale_order "
                   "WHERE incoterm IS NOT NULL LIMIT 1")
    if env.cr.fetchone():
        env.ref('base.group_user').write({
            'implied_ids': [(4, env.ref('sale.group_display_incoterm').id)]
        })


def set_invoice_incoterms_id(env):
    """ Propagate existing incoterms on sale order to related invoices """
    openupgrade.logged_query(
        env.cr, """\
        UPDATE account_invoice ai
        SET incoterms_id = so.incoterm
        FROM sale_order so
        JOIN sale_order_line sol ON sol.order_id = so.id
        JOIN sale_order_line_invoice_rel rel ON sol.id = rel.order_line_id
        JOIN account_invoice_line ail ON rel.invoice_line_id = ail.id
        WHERE ai.id = ail.invoice_id
            AND so.incoterm IS NOT NULL;""")


def set_product_template_invoice_policy_delivery(env):
    """ Obsolete field 'invoice_state' from stock_account in 8.0 is replaced
    by a specific value for product_template.invoice_policy in this module.

    We only look at the most recent stock moves that satisfy the criteria."""
    openupgrade.logged_query(
        env.cr, """\
        UPDATE product_template pt
        SET invoice_policy = 'delivery'
        FROM product_product pp
        JOIN stock_move sm ON sm.product_id = pp.id
        JOIN (SELECT product_id, max(sm_sub.create_date) maxDate
              FROM stock_move sm_sub
              JOIN stock_location sl ON sm_sub.location_dest_id = sl.id
                 AND sl.usage = 'customer' AND NOT sl.scrap_location
              GROUP BY product_id) sm_date
            ON sm.product_id = sm_date.product_id
                AND sm.create_date = sm_date.maxDate
        WHERE pt.id = pp.product_tmpl_id
            AND sm.%s != 'none'""",
        (AsIs(openupgrade.get_legacy_name('invoice_state')),))


def set_sale_order_qty_delivered(env):
    loc_ids = tuple(env['stock.location'].search(
        [('usage', '=', 'customer'),
         ('scrap_location', '=', False)]).ids)
    if not loc_ids:
        return
    openupgrade.logged_query(
        env.cr, """\
        UPDATE sale_order_line sol
        SET qty_delivered = qty
        FROM (
            SELECT sol.id AS line_id, SUM(sm.product_uom_qty) AS qty
            FROM sale_order_line sol
                JOIN procurement_order po ON po.sale_line_id = sol.id
                JOIN stock_move sm ON sm.procurement_id = po.id
            WHERE sm.state = 'done'
                AND sm.product_uom = sol.product_uom
                AND sm.location_dest_id in %s
            GROUP by sol.id) a
         WHERE sol.id = line_id""", (loc_ids,))
    # Take only records that have the same products on both move and
    # sale order lines as unit categories could be different if
    # bom (phantom) are used.
    env.cr.execute("""\
        SELECT sol.id, sm.id
        FROM sale_order_line sol
            JOIN procurement_order po ON po.sale_line_id = sol.id
            JOIN stock_move sm ON sm.procurement_id = po.id
        WHERE sm.state = 'done'
            AND sm.product_uom != sol.product_uom
            AND sm.product_id = sol.product_id
            AND sm.location_dest_id in %s""", (loc_ids,))
    so_qty_map = {}
    uom_obj = env['product.uom']

    for line_id, move_id in env.cr.fetchall():
        line = env['sale.order.line'].browse(line_id)
        move = env['stock.move'].browse(move_id)
        so_qty_map.setdefault(line_id, line.qty_delivered)
        so_qty_map[line_id] += uom_obj._compute_qty_obj(
            move.product_uom, move.product_uom_qty, line.product_uom)

    if so_qty_map:
        openupgrade.logged_query(
            env.cr, """\
            UPDATE sale_order_line sol
                SET qty_delivered = data.qty_delivered
            FROM (values %s) AS data(line_id, qty_delivered)
            WHERE data.line_id = sol.id""" % ','.join(
                [str(tpl) for tpl in so_qty_map.iteritems()]))
