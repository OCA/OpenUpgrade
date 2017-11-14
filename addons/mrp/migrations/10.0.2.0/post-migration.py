# -*- coding: utf-8 -*-
# © 2017 Paul Catinean <https://www.pledra.com>
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_defaults(env):
    # Set default values from field definition as this is a new field and
    # the default val resembles the previous behavior best
    default_specs = {
        'mrp.bom': [('ready_to_produce', None)],
        'mrp.routing.workcenter': [('batch', None)],
        'mrp.workcenter': [('sequence', None)],
    }
    openupgrade.set_defaults(env.cr, env, default_specs)


def map_mrp_production_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'), 'state',
        [('draft', 'confirmed'),
         ('in_production', 'progress'),
         ('ready', 'planned'),
         ], table='mrp_production', write='sql')


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


def update_stock_warehouse(cr):
    cr.execute(
        """
        UPDATE stock_warehouse
        SET manufacture_to_resupply = TRUE
        """
    )


def populate_production_picking_type_id(cr):
    cr.execute(
        """
        UPDATE mrp_production mp
        SET picking_type_id = spt.id
        FROM (
            SELECT min(id) as id, default_location_dest_id
            FROM stock_picking_type
            WHERE code = 'mrp_operation'
            GROUP BY default_location_dest_id
        ) spt
        WHERE mp.location_dest_id = spt.default_location_dest_id
            AND mp.picking_type_id IS NULL
        """
    )
    cr.execute(
        """
        UPDATE mrp_production mp
        SET picking_type_id = spt.id
        FROM (
            SELECT id
            FROM stock_picking_type
            WHERE code = 'mrp_operation'
            LIMIT 1
        ) spt
        WHERE mp.picking_type_id IS NULL
        """
    )


def populate_routing_workcenter_routing_id(cr):
    cr.execute(
        """
        SELECT COUNT(id)
        FROM mrp_routing
        """
    )
    if cr.fetchall()[0][0] == 0:
        cr.execute(
            """
            INSERT INTO mrp_routing (id, name, active)
            VALUES (1, 'Dummy routing', TRUE)
            """
        )
    cr.execute(
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
    cr.execute(
        """
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
    quants = cr.fetchall()
    for quant in quants:
        cr.execute(
            """
            INSERT INTO stock_quant_consume_rel
            VALUES %s, %s
            """ % (quant[0], quant[1])
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    fill_defaults(env)
    map_mrp_production_state(cr)
    map_mrp_workorder_state(cr)
    update_stock_warehouse(cr)
    populate_production_picking_type_id(cr)
    populate_routing_workcenter_routing_id(cr)
    fill_stock_quant_consume_rel(cr)
    openupgrade.load_data(
        cr, 'mrp', 'migrations/10.0.2.0/noupdate_changes.xml')
