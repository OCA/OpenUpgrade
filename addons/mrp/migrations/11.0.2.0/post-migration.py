# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def fill_mrp_document(cr):
    cr.execute(
        """
        INSERT INTO mrp_document (ir_attachment_id, active, priority,
            create_uid, create_date, write_uid, write_date)
        SELECT ia.id, TRUE as active, ia.%s,
            ia.create_uid, ia.create_date, ia.write_uid, ia.write_date
        FROM ir_attachment ia
        LEFT JOIN (
            SELECT count(mbl.id) as num_mbl, pp.id as pp_id, pt.id as pt_id
            FROM mrp_bom_line mbl
            LEFT JOIN product_product pp ON mbl.product_id = pp.id
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            GROUP BY pp_id, pt_id
        ) mbl ON ((ia.res_model = 'product.product' AND ia.res_id = mbl.pp_id)
            OR (ia.res_model = 'product.template' AND ia.res_id = mbl.pt_id))
        WHERE mbl.num_mbl IS NOT NULL AND res_field IS NULL
        """, (AsIs(openupgrade.get_legacy_name('priority')), ),
    )


@openupgrade.logging()
def create_stock_move_lines_from_stock_move_lots(env):
    """In mrp module, stock.move.lots model was renamed to
    stock.pack.operations before becoming stock.move.lines.
    So we need to create also stock move lines from stock move lots."""
    insert_into = """create_date,
            create_uid,
            date,
            location_dest_id,
            location_id,
            lot_id,
            lot_name,
            move_id,
            ordered_qty,
            owner_id,
            picking_id,
            product_id,
            product_qty,
            product_uom_id,
            product_uom_qty,
            qty_done,
            reference,
            state,
            write_date,
            write_uid,
            done_move,
            done_wo,
            lot_produced_id,
            lot_produced_qty,
            production_id,
            workorder_id"""
    select = """current_timestamp,
            sm.write_uid,
            sm.date::date,
            sm.location_dest_id,
            sm.location_id,
            sml.lot_id,
            spl.name,
            sm.id,
            sm.%s,
            sm.restrict_partner_id,
            sm.picking_id,
            sm.product_id,
            CASE WHEN sm.is_done = TRUE THEN 0
            ELSE sm.product_qty
            END as product_qty,
            sm.product_uom,
            CASE WHEN sm.is_done = TRUE THEN 0
            ELSE sm.product_uom_qty
            END as product_uom_qty,
            sm.product_uom_qty as qty_done,
            sm.name,
            sm.state,
            current_timestamp,
            sm.write_uid,
            sm.is_done,
            COALESCE(sml.done_wo, TRUE),
            sml.lot_produced_id,
            sml.lot_produced_qty,
            sm.raw_material_production_id,
            sml.workorder_id""" % openupgrade.get_legacy_name(
        'quantity_done_store')
    from_ = """stock_move sm
        INNER JOIN mrp_production mp ON sm.raw_material_production_id = mp.id
        LEFT JOIN stock_move_lots sml ON (sml.move_id = sm.id
            AND sml.production_id = mp.id)
        LEFT JOIN stock_production_lot spl ON sml.lot_id = spl.id"""
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_move_line (%(insert_into)s
        )
        SELECT %(select)s
        FROM %(from)s
        WHERE sm.state NOT IN ('cancel', 'confirmed')
            AND sm.id NOT IN (SELECT sq.reservation_id
                              FROM stock_quant sq
                              WHERE sq.reservation_id IS NOT NULL)
        """ % {
            'insert_into': insert_into,
            'select': select,
            'from': from_,
        },
    )
    select = """current_timestamp,
            sm.write_uid,
            sm.date::date,
            sm.location_dest_id,
            sm.location_id,
            sml.lot_id,
            spl.name,
            sm.id,
            0,
            sm.restrict_partner_id,
            sm.picking_id,
            sm.product_id,
            0,
            sm.product_uom,
            0,
            sm.product_uom_qty as qty_done,
            sm.name,
            sm.state,
            current_timestamp,
            sm.write_uid,
            sm.is_done,
            TRUE,
            sml.lot_produced_id,
            sml.lot_produced_qty,
            NULL,
            sml.workorder_id"""
    from_ = """stock_move sm
        INNER JOIN mrp_production mp ON sm.production_id = mp.id
        LEFT JOIN stock_move_lots sml ON (sml.move_id = sm.id
            AND sml.production_id = mp.id)
        LEFT JOIN stock_production_lot spl ON sml.lot_id = spl.id"""
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_move_line (%(insert_into)s
        )
        SELECT %(select)s
        FROM %(from)s
        WHERE sm.state NOT IN ('cancel', 'confirmed')
            AND sm.id NOT IN (SELECT sq.reservation_id
                              FROM stock_quant sq
                              WHERE sq.reservation_id IS NOT NULL)
        """ % {
            'insert_into': insert_into,
            'select': select,
            'from': from_,
        },
    )


def update_stock_move_line_production_id(env):
    """Add the production_id field to stock move lines associated to
    a stock move that is the raw material of an mrp.production"""
    openupgrade.logged_query(env.cr, """
        UPDATE stock_move_line AS sml
        SET production_id = sm.raw_material_production_id
        FROM stock_move AS sm
        WHERE sml.move_id = sm.id
        AND sm.raw_material_production_id IS NOT NULL
    """)


def fill_stock_move_line_consume_rel(cr):
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO stock_move_line_consume_rel (consume_line_id,
            produce_line_id)
        SELECT DISTINCT sml1.id, sml2.id
        FROM stock_quant_consume_rel sqcr
        INNER JOIN stock_quant_move_rel sqmr1
            ON sqmr1.quant_id = sqcr.consume_quant_id
        INNER JOIN stock_quant_move_rel sqmr2
            ON sqmr2.quant_id = sqcr.produce_quant_id
        INNER JOIN stock_move_line sml1
            ON sml1.move_id = sqmr1.move_id
        INNER JOIN stock_move_line sml2
            ON sml2.move_id = sqmr2.move_id
        WHERE NOT EXISTS (
            SELECT *
            FROM stock_move_line_consume_rel
            WHERE consume_line_id = sml1.id
                AND produce_line_id = sml2.id
        )
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    fill_mrp_document(cr)
    create_stock_move_lines_from_stock_move_lots(env)
    update_stock_move_line_production_id(env)
    fill_stock_move_line_consume_rel(cr)
    openupgrade.load_data(
        cr, 'mrp', 'migrations/11.0.2.0/noupdate_changes.xml',
    )
