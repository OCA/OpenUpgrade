# -*- coding: utf-8 -*-
# © 2017 Paul Catinean <https://www.pledra.com>
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


def populate_stock_move_quantity_done_store(cr):
    cr.execute(
        """
        UPDATE stock_move
        SET quantity_done_store = product_uom_qty
        WHERE state = 'done'
            AND (COALESCE(production_id, 0) > 0
                OR COALESCE(raw_material_production_id, 0) > 0)
        """
    )


def archive_mrp_bom_date_stop(cr):
    cr.execute(
        """
        UPDATE mrp_bom
        SET active = FALSE
        WHERE active = TRUE AND %s IS NOT NULL AND %s < '%s'
        """ % (openupgrade.get_legacy_name('date_stop'),
               openupgrade.get_legacy_name('date_stop'),
               time.strftime(DEFAULT_SERVER_DATE_FORMAT),
               )
    )


def update_mrp_workorder_hour(cr):
    """It's a sum because the user used hours or used cycles."""
    cr.execute(
        """
        UPDATE mrp_workorder
        SET duration_expected = (COALESCE(%s, 0) + COALESCE(%s, 0)) * 60
        """ % (openupgrade.get_legacy_name('hour'),
               openupgrade.get_legacy_name('cycle'),
               )
    )


def update_mrp_workcenter_times(cr):
    """The time now in minutes instead of hours."""
    cr.execute(
        """
        UPDATE mrp_workcenter
        SET time_start = COALESCE(time_start, 0) * 60,
            time_stop = COALESCE(time_stop, 0) * 60
        """
    )


def fill_mrp_routing_workcenter_time_cycle_manual(cr):
    cr.execute(
        """
        UPDATE mrp_routing_workcenter
        SET time_cycle_manual = COALESCE(%s, 0) * COALESCE(%s, 1) * 60
        """ % (openupgrade.get_legacy_name('hour_nbr'),
               openupgrade.get_legacy_name('cycle_nbr'),
               )
    )


def map_mrp_production_state(cr):
    """Get ids of old 'draft' MOs and map states.
    :return: list of ids with all old draft MOs.
    """
    cr.execute(
        """
        SELECT id
        FROM mrp_production
        WHERE state = 'draft'
        """
    )
    draft_ids = [r[0] for r in cr.fetchall()]
    # only MOs that uses workorders have the 'planned' state:
    cr.execute(
        """
        UPDATE mrp_production mp
        SET state = 'planned'
        FROM mrp_workorder mw
        WHERE mp.state = 'confirmed'
            AND mp.id = mw.production_id
        """
    )
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'), 'state',
        [('draft', 'confirmed'),
         ('in_production', 'progress'),
         ('ready', 'planned'),
         ], table='mrp_production', write='sql')
    return draft_ids


def create_moves_draft_mos(env, draft_ids):
    env['mrp.production'].browse(draft_ids)._generate_moves()


def map_mrp_workorder_state(cr):
    legacy_state = openupgrade.get_legacy_name('state')
    if openupgrade.column_exists(cr, 'mrp_workorder', legacy_state):
        openupgrade.map_values(
            cr,
            legacy_state, 'state',
            [('draft', 'pending'),
             ('starworking', 'progress'),
             ('pause', 'ready'),
             ], table='mrp_workorder', write='sql')


def update_stock_warehouse(env):
    """Check for manufacturing warehouses and update them.
    :returns: a map (dict) to populate MO's picking types.
              keys: location_dest_id
              values: corresponding manu_type_id
    """
    cr = env.cr
    cr.execute(
        """
        SELECT location_dest_id
        FROM mrp_production
        GROUP BY location_dest_id
        """
    )
    ids = [r[0] for r in cr.fetchall()]
    loc_ids = env['stock.location'].browse(ids)
    wh_ids = []
    loc_wh_map = dict()
    for loc in loc_ids:
        wh_id = loc.get_warehouse()
        if wh_id:
            wh_ids.append(wh_id.id)
            loc_wh_map[loc.id] = wh_id.id
    # update manufacture_to_ressupply
    if wh_ids:
        cr.execute(
            """
            UPDATE stock_warehouse
            SET manufacture_to_resupply = TRUE
            WHERE id in %s
            """, (tuple(set(wh_ids)),)
        )
    # Create a default picking_type for manufacturing, for each warehouse above
    loc_pt_map = dict()
    wh_pt_map = dict()
    for wh in env["stock.warehouse"].browse(list(set(wh_ids))):
        wh._create_manufacturing_picking_type()
        wh_pt_map[wh.id] = wh.manu_type_id.id
    for loc in loc_wh_map.keys():
        loc_pt_map[loc] = wh_pt_map[loc_wh_map[loc]]
    return loc_pt_map


def populate_production_picking_type_id(cr, loc_pt_map):
    """
    Updated all MO's with the new picking type created by
    'update_stock_warehouse'.
    """
    for loc in loc_pt_map.keys():
        openupgrade.logged_query(
            cr,
            """
            UPDATE mrp_production
            SET picking_type_id = %s
            WHERE location_dest_id = %s
                AND picking_type_id IS NULL
            """ % (loc_pt_map[loc], loc)
        )


def update_manufacture_procurement_rules(cr):
    cr.execute(
        """
        UPDATE procurement_rule pr
        SET picking_type_id = spt.id
        FROM stock_picking_type spt
        WHERE pr.action='manufacture' AND spt.code='mrp_operation'
            AND pr.warehouse_id = spt.warehouse_id
        """
    )


def populate_routing_workcenter_routing_id(env):
    routing = env['mrp.routing'].search([], limit=1)
    if not routing:
        env['mrp.routing'].create({
            'name': 'Dummy routing',
            'active': True,
        })
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mrp_routing_workcenter mrw
        SET routing_id = routing.id
        FROM (
            SELECT id
            FROM mrp_routing
            LIMIT 1
        ) routing
        WHERE mrw.routing_id IS NULL
        """
    )


def fill_stock_quant_consume_rel(cr):
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO stock_quant_consume_rel
        SELECT DISTINCT sqmr_consumed.quant_id, sqmr_produced.quant_id
        FROM stock_move sm_consumed
        INNER JOIN stock_move sm_produced
            ON sm_consumed.%s = sm_produced.id
        INNER JOIN stock_quant_move_rel sqmr_consumed
            ON sqmr_consumed.move_id = sm_consumed.id
        INNER JOIN stock_quant_move_rel sqmr_produced
            ON sqmr_produced.move_id = sm_produced.id
        """ % openupgrade.get_legacy_name('consumed_for')
    )


def populate_stock_move_workorder_id(cr):
    # put in order the workorders
    openupgrade.logged_query(
        cr,
        """
        UPDATE mrp_workorder mw
        SET next_work_order_id = Q4.next_id
        FROM (
            SELECT Q1.id as id, min(Q2.sequence) as sequence
            FROM (
                SELECT id, production_id, %s as sequence
                FROM mrp_workorder
            ) Q1
            INNER JOIN (
                SELECT id, production_id, %s as sequence
                FROM mrp_workorder
                WHERE production_id IS NOT NULL
            ) Q2 ON (
                ((Q1.sequence < Q2.sequence) OR ((Q1.sequence = Q2.sequence)
                AND (Q1.id < Q2.id))) AND Q1.production_id = Q2.production_id
            )
            GROUP BY Q1.id
        ) Q3
        LEFT JOIN (
            SELECT Q1.id as id, min(Q2.id) as next_id, Q2.sequence
            FROM (
                SELECT id, production_id, %s as sequence
                FROM mrp_workorder
            ) Q1
            INNER JOIN (
                SELECT id, production_id, %s as sequence
                FROM mrp_workorder
                WHERE production_id IS NOT NULL
            ) Q2 ON (
                ((Q1.sequence < Q2.sequence) OR ((Q1.sequence = Q2.sequence)
                AND (Q1.id < Q2.id))) AND Q1.production_id = Q2.production_id
            )
            GROUP BY Q1.id, Q2.sequence
        ) Q4 ON Q3.id = Q4.id AND Q3.sequence = Q4.sequence
        WHERE mw.id = Q3.id
        """ % (openupgrade.get_legacy_name('sequence'),
               openupgrade.get_legacy_name('sequence'),
               openupgrade.get_legacy_name('sequence'),
               openupgrade.get_legacy_name('sequence'))
    )
    # fill stock_move
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_move sm
        SET workorder_id = mw.id
        FROM mrp_production mp
        LEFT JOIN mrp_workorder mw ON (
            mw.production_id = mp.id AND mw.next_work_order_id IS NULL
        )
        WHERE sm.raw_material_production_id = mp.id AND mw.id IS NOT NULL
        """
    )


def fill_stock_move_unit_factor(env):
    cr = env.cr
    productions = env['mrp.production'].search([])
    if openupgrade.column_exists(cr, 'mrp_production', 'qty_produced'):
        cr.execute(
            """
            SELECT id
            FROM mrp_production
            WHERE qty_produced IS NULL
            """
        )
        ids = [r[0] for r in cr.fetchall()]
        productions = env['mrp.production'].browse(ids)
    productions._get_produced_qty()

    for production in productions.filtered(
            lambda r: r.state not in ['done', 'cancel']):
        diff = production.product_qty - production.qty_produced
        cr.execute(
            """
            UPDATE stock_move sm
            SET unit_factor = CASE
                WHEN %s = 0.0
                THEN sm.product_uom_qty
                WHEN %s != 0.0
                THEN sm.product_uom_qty / %s
                ELSE unit_factor
            END
            WHERE sm.raw_material_production_id = %s
            """ % (diff, diff, diff,
                   production.id,
                   )
        )


def fill_stock_move_bom_line_id(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_move sm_update
        SET bom_line_id = mbl.bom_line_id
        FROM stock_move sm
            INNER JOIN mrp_production mp
            ON sm.raw_material_production_id = mp.id
            LEFT JOIN (
                SELECT min(id) AS bom_line_id, bom_id, product_id
                FROM mrp_bom_line
                GROUP BY bom_id, product_id
                ) mbl ON (
                    mbl.bom_id = mp.bom_id
                    AND mbl.product_id = sm.product_id)
        WHERE sm_update.raw_material_production_id = mp.id
            AND sm_update.id = sm.id
            AND sm_update.bom_line_id IS NULL;
        """
    )


def populate_mrp_workcenter_productivity(env):
    cr = env.cr
    cr.execute(
        """
        SELECT id
        FROM mrp_workcenter_productivity_loss
        WHERE sequence = 0
        LIMIT 1
        """
    )
    loss_id = cr.fetchone()[0]
    if not loss_id:
        cr.execute(
            """
            SELECT id
            FROM mrp_workcenter_productivity_loss
            ORDER BY id ASC
            LIMIT 1
            """
        )
        loss_id = cr.fetchone()[0]
        if not loss_id:
            loss_id = env['mrp.workcenter.productivity.loss'].create({
                'name': 'Dummy Loss',
                'loss_type': 'productive',
            }).id
    legacy_delay = openupgrade.get_legacy_name('delay')
    if openupgrade.column_exists(cr, 'mrp_workorder', legacy_delay):
        openupgrade.logged_query(
            cr,
            """
            INSERT INTO mrp_workcenter_productivity
            (user_id, create_uid, create_date, write_uid, write_date,
            loss_id, date_start, date_end, workorder_id, workcenter_id)
            SELECT mp.user_id, wo.create_uid, wo.create_date, wo.write_uid,
            wo.write_date, %s loss_id, wo.date_start,
            wo.date_start + (wo.%s || ' hour')::INTERVAL AS date_end,
            wo.id workorder_id, wo.workcenter_id
            FROM mrp_workorder wo
            LEFT JOIN mrp_production mp ON wo.production_id = mp.id
            WHERE wo.state NOT IN ('cancel', 'pending')
            """ % (loss_id,
                   legacy_delay,
                   )
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    populate_stock_move_quantity_done_store(cr)
    archive_mrp_bom_date_stop(cr)
    update_mrp_workorder_hour(cr)
    update_mrp_workcenter_times(cr)
    fill_mrp_routing_workcenter_time_cycle_manual(cr)
    draft_ids = map_mrp_production_state(cr)
    create_moves_draft_mos(env, draft_ids)
    map_mrp_workorder_state(cr)
    loc_pt_map = update_stock_warehouse(env)
    populate_production_picking_type_id(cr, loc_pt_map)
    update_manufacture_procurement_rules(cr)
    populate_routing_workcenter_routing_id(env)
    fill_stock_quant_consume_rel(cr)
    populate_stock_move_workorder_id(cr)
    fill_stock_move_unit_factor(env)
    fill_stock_move_bom_line_id(cr)
    populate_mrp_workcenter_productivity(env)
    openupgrade.load_data(
        cr, 'mrp', 'migrations/10.0.2.0/noupdate_changes.xml')
