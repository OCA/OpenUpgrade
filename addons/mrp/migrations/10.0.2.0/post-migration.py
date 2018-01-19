# -*- coding: utf-8 -*-
# © 2017 Paul Catinean <https://www.pledra.com>
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_mrp_workcenter_times(cr):
    """The time now in minutes instead of hours."""
    cr.execute(
        """
        UPDATE mrp_workcenter
        SET time_start = COALESCE(time_start, 0) * 60,
            time_stop = COALESCE(time_stop, 0) * 60
        """
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
        # if mrp_operations was installed
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
        GROUP BY location_dest_id;
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


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    update_mrp_workcenter_times(cr)
    draft_ids = map_mrp_production_state(cr)
    create_moves_draft_mos(env, draft_ids)
    map_mrp_workorder_state(cr)
    loc_pt_map = update_stock_warehouse(env)
    populate_production_picking_type_id(cr, loc_pt_map)
    populate_routing_workcenter_routing_id(env)
    fill_stock_quant_consume_rel(cr)
    populate_stock_move_workorder_id(cr)
    openupgrade.load_data(
        cr, 'mrp', 'migrations/10.0.2.0/noupdate_changes.xml')
