# -*- coding: utf-8 -*-
# Copyright 2017 Trescloud <http://trescloud.com>
# Copyright 2017 Eficent - Miquel
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def map_location_auto(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('auto'), 'auto',
        [('auto', 'manual')],
        table='stock_location_path', write='sql')


def update_picking_type_id(env):
    """Updates picking_type_id, defaulting to some value, guessing by looking
    at source and destination locations, and warehouse.
    :param env: environment variable (self)
    """
    # load xml data to be used for filling in missing info
    xml_stock_picking_type_int = env.ref("stock.picking_type_internal")
    xml_stock_picking_type_out = env.ref("stock.picking_type_out")
    xml_stock_picking_type_in = env.ref("stock.picking_type_in")
    xml_stock_picking_type_manufacturing = env.ref(
        "mrp.picking_type_manufacturing", False
    )
    # verify for each procurement rule to set
    procurement_rules_to_set = env['procurement.rule'].search([
        ('picking_type_id', '=', False),
    ])
    for procurement_rule in procurement_rules_to_set:
        picking_type_id = False
        env.cr.execute(
            """
            SELECT id from stock_picking_type
            WHERE warehouse_id = %s AND
                default_location_dest_id = %s AND
                default_location_src_id = %s
            """,
            (
                procurement_rule.warehouse_id.id or None,
                procurement_rule.location_id.id or None,
                procurement_rule.location_src_id.id or None,
            )
        )
        picking_type_ids = env.cr.fetchone()
        if picking_type_ids:
            picking_type_id = picking_type_ids[0]
        # fallback values when everything else fails
        if not picking_type_id:
            if procurement_rule.action == 'buy':
                # location_src_id is not considered
                # (as is not mandatory in this case)
                if xml_stock_picking_type_in:
                    picking_type_id = xml_stock_picking_type_in.id
            elif procurement_rule.action == 'move':
                if procurement_rule.location_id and procurement_rule.\
                        location_id.usage == 'customer':
                    # delivery case to a customer location
                    if xml_stock_picking_type_out:
                        picking_type_id = xml_stock_picking_type_out.id
                else:
                    if xml_stock_picking_type_int:
                        picking_type_id = xml_stock_picking_type_int.id
            # special case for mrp module put here for not repeating the
            # logic. If mrp is not installed, it won't break
            elif procurement_rule.action == 'manufacture':
                if xml_stock_picking_type_manufacturing:
                    picking_type_id = xml_stock_picking_type_manufacturing.id
        procurement_rule.picking_type_id = picking_type_id


def update_ordered_qty(cr):
    """ Set the value of new field ordered_qty as:
      - for stock moves the value of field product_uom_qty
      - for stock_pack_operation the value of product_qty
    :param cr: cursor variable (self.env)
    """

    cr.execute(
        "UPDATE stock_move SET ordered_qty = product_uom_qty")
    cr.execute(
        "UPDATE stock_pack_operation SET ordered_qty = product_qty")


def populate_stock_scrap(cr):
    """
    Fills up new object "stock.scrap" based on moves linked to scrap location
    :param cr: cursor variable (self.env)
    """
    cr.execute(
        """
        SELECT id from stock_location
        WHERE scrap_location is True
        """
    )
    scrap_location_ids = cr.fetchone()
    # Use SQL instead of ORM, otherwise stock_scrap.create() will create a
    # duplicated stock move
    cr.execute(
        """
        INSERT INTO stock_scrap
            (date_expected,create_date,location_id,lot_id,move_id,
            name,origin,owner_id,package_id,picking_id,product_id,
            product_uom_id,scrap_location_id,scrap_qty,state)
            WITH Q1 as (SELECT DISTINCT sq.package_id,sr.move_id
                FROM stock_quant_move_rel sr
                INNER JOIN stock_quant as sq ON sq.id = sr.quant_id),
            Q2 as (SELECT COUNT(Q1.package_id) as n,Q1.move_id
                FROM Q1
                GROUP BY Q1.move_id),
            Q3 as (SELECT DISTINCT Q2.move_id,sq.package_id
                FROM Q2
                LEFT JOIN stock_quant_move_rel sr ON sr.move_id = Q2.move_id
                LEFT JOIN stock_quant as sq ON sq.id = sr.quant_id
                WHERE Q2.n = 1)
            SELECT date_expected,create_date,location_id,restrict_lot_id,id,
                name,origin,restrict_partner_id,Q3.package_id,picking_id,
                product_id,product_uom,location_dest_id,product_uom_qty,state
            FROM stock_move sm
            LEFT JOIN Q3 ON sm.id = Q3.move_id
            WHERE location_dest_id IN %s AND state = 'done'
        """, (scrap_location_ids,))


def assign_security_groups(env):
    """Assign the group that has been unfolded in 2 in the new version to the
     users that had the old one.

     Assign also the warning group if the old module is installed.

    :param env: Environment
    """
    users = env['res.users'].search([
        ('groups_id', '=', env.ref('stock.group_stock_multi_locations').id)
    ])
    users.write({
        'groups_id': [(4, env.ref('stock.group_stock_multi_warehouses').id)],
    })
    if openupgrade.is_module_installed(env.cr, 'warning'):
        env['res.users'].search([]).write({
            'groups_id': [(4, env.ref('stock.group_warning_stock').id)],
        })


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    map_location_auto(cr)
    update_picking_type_id(env)
    update_ordered_qty(cr)
    populate_stock_scrap(cr)
    assign_security_groups(env)
    openupgrade.load_data(
        cr, 'stock', 'migrations/10.0.1.1/noupdate_changes.xml',
    )
