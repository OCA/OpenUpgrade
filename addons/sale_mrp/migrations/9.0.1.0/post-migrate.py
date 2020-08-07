# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


def phantom_bom_qty_delivered(env):
    """ Apply Odoo 12 logic to determine if sale lines with phantom bom
    products have been delivered: this is the case if there *are*
    stock moves from non-cancelled pickings, and all of these moves are
    in 'done' state. """
    logger = logging.getLogger('sale_mrp.migrations.9.0.1.1')
    logger.info(
        'Updating qty delivered on sale lines with phantom bom products')
    openupgrade.logged_query(
        env.cr,
        """
        WITH lines AS (
            SELECT DISTINCT(sol.id) FROM sale_order_line sol
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN mrp_bom mb ON mb.type = 'phantom'
                AND (mb.product_id = pp.id
                     OR (mb.product_tmpl_id = pt.id
                     AND mb.product_id is null)))
        UPDATE sale_order_line sol
        SET qty_delivered = CASE
            WHEN EXISTS(
                SELECT po.id FROM procurement_order po
                JOIN stock_move sm ON sm.procurement_id = po.id
                JOIN stock_picking sp ON sm.picking_id = sp.id
                WHERE po.sale_line_id = sol.id
                    AND sp.state != 'cancel') AND NOT EXISTS(
                SELECT po.id FROM procurement_order po
                JOIN stock_move sm ON sm.procurement_id = po.id
                JOIN stock_picking sp ON sm.picking_id = sp.id
                WHERE po.sale_line_id = sol.id
                    AND sp.state != 'cancel'
                    AND sm.state != 'done')
            THEN product_uom_qty
            ELSE 0.0
        END
        WHERE sol.id IN (SELECT id FROM lines)
        """)


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    phantom_bom_qty_delivered(env)
