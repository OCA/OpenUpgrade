# Copyright 2021 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_stock_move_bom_line_id(env):
    """v13 added a new functionality to this bom_line_id field.
    Apart from the usual value for raw moves in mrp productions,
    now this field has a value for receipts moves generated from a kit.
    See _prepare_phantom_move_values method, that has bom_line_id field."""
    openupgrade.logged_query(
        env.cr, """
    UPDATE stock_move sm0
    SET bom_line_id = mbl0.id
    FROM (
        SELECT moves.id, moves.product_id,
            (array_agg(moves.bom_id))[1] as bom_id
        FROM (
            SELECT sm.id, mb.id AS bom_id, sm.product_id
            FROM stock_move sm
            JOIN stock_picking_type spt ON (
                sm.picking_type_id = spt.id AND spt.code = 'incoming')
            JOIN product_product pp ON sm.product_id = pp.id
            JOIN product_template pt ON (
                pp.product_tmpl_id = pt.id AND pt.type != 'service')
            JOIN mrp_bom_line mbl ON mbl.product_id = pp.id
            JOIN mrp_bom mb ON (mbl.bom_id = mb.id AND mb.active
                AND (mb.company_id IS NULL OR mb.company_id = sm.company_id)
                AND mb.type = 'phantom')
            JOIN purchase_order_line pol ON sm.purchase_line_id = pol.id
            JOIN product_product pp2 ON pol.product_id = pp2.id
            JOIN product_template pt2 ON pp2.product_tmpl_id = pt2.id
            WHERE sm.bom_line_id IS NULL AND sm.product_id != pol.product_id
                AND (pp2.id = mb.product_id OR
                (mb.product_id IS NULL AND pt2.id = mb.product_tmpl_id))
            ORDER BY sm.id, mb.company_id, mb.sequence,
                mb.product_id, mb.product_tmpl_id
        ) moves
        GROUP BY moves.id, moves.product_id
    ) rel
    JOIN mrp_bom_line mbl0 ON (
        rel.bom_id = mbl0.bom_id AND mbl0.product_id = rel.product_id)
    WHERE sm0.id = rel.id""")


@openupgrade.migrate()
def migrate(env, version):
    fill_stock_move_bom_line_id(env)
