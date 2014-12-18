# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ONESTEin B.V.
#              (C) 2014 Therp B.V.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from openerp.openupgrade import openupgrade, openupgrade_80
from openerp.modules.registry import RegistryManager
from openerp import pooler, SUPERUSER_ID

logger = logging.getLogger('OpenUpgrade.stock')
default_spec = {
    'procurement.rule': [
        ('procure_method', 'make_to_stock'),
    ],
    'product.putaway': [
        ('method', 'fixed'),
    ],
    'stock.inventory': [
        ('filter', 'none'),
        ('location_id', False),
    ],
    'stock.move': [
        ('procure_method', 'make_to_stock',),
    ],
}


def default_stock_location(cr, pool, uid):
    try:
        warehouse = pool['ir.model.data'].get_object(cr, uid, 'stock', 'warehouse0')
        result = default_spec['stock_inventory']
        result = [
            result[0], ('location_id', warehouse.lot_stock_id.id)
        ]
        return result
    except:
        message = "Failed to get the default warehouse, using default_spec."
        openupgrade.message(cr, 'stock', 'stock_inventory', 'location_id', message)
        result = default_spec['stock.inventory']
        return result


def migrate_product(cr, pool):
    """Migrate track_incoming, track_outgoing"""
    prod_tmpl_obj = pool['product.template']
    for field in 'track_incoming', 'track_outgoing':
        cr.execute(
            """
            SELECT product_tmpl_id FROM product_product
            WHERE {} IS TRUE""".format(
                openupgrade.get_legacy_name(field)))
        template_ids = [row[0] for row in cr.fetchall()]
        logger.debug(
            "Setting %s to True for %s product templates",
            field, len(template_ids))
        prod_tmpl_obj.write(
            cr, SUPERUSER_ID, template_ids, {field: True})


def swap_procurement_move_rel(cr, pool):
    """Procurement_order.move_id is swapped to stock_move.procurement_id.
    So instead of a m2o from procurement_order, it is a m2o from stock_move in version 8.
    """
    uid = SUPERUSER_ID
    stock_move_obj = pool['stock.move']

    move_legacy = openupgrade.get_legacy_name('move_id')
    sql = """SELECT id, {} FROM {}""".format(move_legacy, 'procurement_order')
    cr.execute(sql)
    proc_order_rows = cr.fetchall()
    for proc_order_id, move_id in proc_order_rows:
        if move_id and proc_order_id:
            stock_move_obj.write(cr, uid, move_id, {'procurement_id': proc_order_id})


def restore_move_inventory_rel(cr, pool):
    uid = SUPERUSER_ID
    simr_legacy = openupgrade.get_legacy_name('stock_inventory_move_rel')
    stock_move_obj = pool['stock.move']
    cr.execute("""SELECT inventory_id, move_id FROM {}""".format(simr_legacy))
    rows = cr.fetchall()
    for inv_id, move_id in rows:
        stock_move_obj.write(cr, uid, move_id, {'inventory_id': inv_id})


def migrate_stock_location(cr):
    """Create a Push rule for each pair of locations linked
    :param cr:
    """
    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    path_obj = pool.get('stock.location.path')
    location_obj = pool.get('stock.location')
    warehouse_obj = pool['stock.warehouse']

    head_sql = """SELECT id, %s, %s, %s, %s, name, %s
        FROM stock_location""" % (
        openupgrade.get_legacy_name('chained_location_id'),
        openupgrade.get_legacy_name('chained_auto_packing'),
        openupgrade.get_legacy_name('chained_company_id'),
        openupgrade.get_legacy_name('chained_delay'),
        openupgrade.get_legacy_name('chained_picking_type'))

    tail_sql = """ WHERE %s is not null""" % (openupgrade.get_legacy_name('chained_location_id'))
    cr.execute(head_sql + tail_sql)

    for location in cr.fetchall():
        loc = location_obj.browse(cr, uid, location[1])
        vals = {
            'active': True,
            'propagate': True,
            'location_from_id': location[0],
            'location_dest_id': location[1],
            'auto': location[2],
            'company_id': location[3],
            'delay': location[4],
            'name': location[5] + ' -> ' + loc.name,
        }

        args = location[3] and [('company_id', '=', location[3])] or []
        vals['warehouse_id'] = warehouse_obj.search(cr, uid, args)[0]
        warehouse = warehouse_obj.browse(cr, uid, vals['warehouse_id'])

        if location[6] == 'in':
            vals['picking_type_id'] = warehouse.in_type_id.id
        elif location[6] == 'out':
            vals['picking_type_id'] = warehouse.out_type_id.id
        else:
            vals['picking_type_id'] = warehouse.int_type_id.id

        path_obj.create(cr, uid, vals)


def migrate_stock_picking(cr):
    """Update picking records with the correct picking_type_id and state
    :param cr:
    """
    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)

    data_obj = pool.get('ir.model.data')
    warehouse = data_obj.get_object(cr, uid, 'stock', 'warehouse0')

    type_legacy = openupgrade.get_legacy_name('type')
    in_id = warehouse.in_type_id.id
    out_id = warehouse.out_type_id.id
    int_id = warehouse.int_type_id.id

    # Fill picking_type_id required field
    for type, type_id in (('in', in_id), ('out', out_id), ('internal', int_id)):
        cr.execute("""UPDATE stock_picking SET picking_type_id = %%s WHERE %s = %%s""" % type_legacy, (type_id, type,))

    # state key auto -> waiting
    cr.execute("""UPDATE stock_picking SET state = %s WHERE state = %s""", ('waiting', 'auto',))


def _migrate_stock_warehouse(cr, id):
    """Warehouse adaptation to the new functionality. Sequences, Picking types, Rules, Paths..
    :param cr: Database cursor
    """
    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    vals = {}

    # Required field: Code
    cr.execute("""UPDATE stock_warehouse SET code = %s where id = %s""", ('WH'+str(id), id,))
    cr.commit()

    data_obj = pool['ir.model.data']
    location_obj = pool['stock.location']
    warehouse_obj = pool['stock.warehouse']
    picking_type_obj = pool['stock.picking.type']
    seq_obj = pool['ir.sequence']

    warehouse = warehouse_obj.browse(cr, uid, id)
    warehouse.refresh()

    # Parent View
    if not warehouse.lot_stock_id.location_id:
        wh_loc_id = location_obj.create(cr, uid, {
            'name': warehouse.code,
            'usage': 'view',
            'location_id': data_obj.get_object_reference(cr, uid, 'stock', 'stock_location_locations')[1]
        })
        vals['view_location_id'] = wh_loc_id
    else:
        vals['view_location_id'] = warehouse.lot_stock_id.location_id.id

    # Sub Locations
    sub_locations = []
    if not warehouse.wh_input_stock_loc_id:
        sub_locations.append({
            'name': 'Input', 'active': warehouse.reception_steps != 'one_step', 'field': 'wh_input_stock_loc_id'
        })

    if not warehouse.wh_output_stock_loc_id:
        sub_locations.append({
            'name': 'Output', 'active': warehouse.delivery_steps != 'ship_only', 'field': 'wh_output_stock_loc_id'
        })

    sub_locations.append({
        'name': 'Quality Control', 'active': warehouse.reception_steps == 'three_steps', 'field': 'wh_qc_stock_loc_id'
    })
    sub_locations.append({
        'name': 'Packing Zone', 'active': warehouse.delivery_steps == 'pick_pack_ship', 'field': 'wh_pack_stock_loc_id'
    })

    for values in sub_locations:
        location_id = location_obj.create(cr, uid, {
            'name': values['name'],
            'usage': 'internal',
            'location_id': vals['view_location_id'],
            'active': values['active'],
        })
        vals[values['field']] = location_id

    # create new sequences
    in_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence in', 'prefix': warehouse.code + '/IN/', 'padding': 5
    })
    out_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence out', 'prefix':  warehouse.code + '/OUT/', 'padding': 5
    })
    int_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence internal', 'prefix': warehouse.code + '/INT/', 'padding': 5
    })
    pack_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence packing', 'prefix': warehouse.code + '/PACK/', 'padding': 5
    })
    pick_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence picking', 'prefix': warehouse.code + '/PICK/', 'padding': 5
    })

    # get default locations
    wh_stock_loc = warehouse.lot_stock_id
    wh_input_stock_loc = warehouse.wh_input_stock_loc_id or vals['wh_input_stock_loc_id']
    wh_output_stock_loc = warehouse.wh_output_stock_loc_id or vals['wh_output_stock_loc_id']
    wh_pack_stock_loc = vals['wh_pack_stock_loc_id']
    customer_loc = data_obj.get_object_reference(cr, uid, 'stock', 'stock_location_customers')[1]
    supplier_loc = data_obj.get_object_reference(cr, uid, 'stock', 'stock_location_suppliers')[1]
    input_loc = wh_input_stock_loc
    if warehouse.reception_steps == 'one_step':
        input_loc = wh_stock_loc.id
    output_loc = wh_output_stock_loc
    if warehouse.delivery_steps == 'ship_only':
        output_loc = wh_stock_loc.id

    in_type_id = picking_type_obj.create(cr, uid, vals={
        'name': 'Receptions',
        'warehouse_id': warehouse.id,
        'code': 'incoming',
        'sequence_id': in_seq_id,
        'default_location_src_id': supplier_loc,
        'default_location_dest_id': input_loc,
        'sequence': 1,
    })
    out_type_id = picking_type_obj.create(cr, uid, vals={
        'name': 'Delivery Orders',
        'warehouse_id': warehouse.id,
        'code': 'outgoing',
        'sequence_id': out_seq_id,
        'return_picking_type_id': in_type_id,
        'default_location_src_id': output_loc,
        'default_location_dest_id': customer_loc,
        'sequence': 4,
    })
    picking_type_obj.write(cr, uid, [in_type_id], {'return_picking_type_id': out_type_id})

    int_type_id = picking_type_obj.create(cr, uid, vals={
        'name': 'Internal Transfers',
        'warehouse_id': warehouse.id,
        'code': 'internal',
        'sequence_id': int_seq_id,
        'default_location_src_id': wh_stock_loc.id,
        'default_location_dest_id': wh_stock_loc.id,
        'active': True,
        'sequence': 2,
    })
    pack_type_id = picking_type_obj.create(cr, uid, vals={
        'name': 'Pack',
        'warehouse_id': warehouse.id,
        'code': 'internal',
        'sequence_id': pack_seq_id,
        'default_location_src_id': wh_pack_stock_loc,
        'default_location_dest_id': output_loc,
        'active': warehouse.delivery_steps == 'pick_pack_ship',
        'sequence': 3,
    })
    pick_type_id = picking_type_obj.create(cr, uid, vals={
        'name': 'Pick',
        'warehouse_id': warehouse.id,
        'code': 'internal',
        'sequence_id': pick_seq_id,
        'default_location_src_id': wh_stock_loc.id,
        'default_location_dest_id': wh_pack_stock_loc,
        'active': warehouse.delivery_steps != 'ship_only',
        'sequence': 2,
    })

    vals['in_type_id'] = in_type_id
    vals['out_type_id'] = out_type_id
    vals['pack_type_id'] = pack_type_id
    vals['pick_type_id'] = pick_type_id
    vals['int_type_id'] = int_type_id,

    # Write picking types on WH.
    warehouse_obj.write(cr, uid, [warehouse.id], vals=vals)
    warehouse.refresh()

    # update ir_model_data references to the main warehouse
    # Reference used in the code for some default values
    if warehouse.code == 'WH1' and in_type_id:
        cr.execute("""UPDATE ir_model_data set noupdate = %s, res_id = %s where name = %s""",
                   (True, in_type_id, 'picking_type_in',))

    # create routes and push/pull rules
    new_objects_dict = warehouse_obj.create_routes(cr, uid, warehouse.id, warehouse)
    warehouse_obj.write(cr, uid, warehouse.id, new_objects_dict)


def migrate_stock_warehouse(cr):
    """Migrate all the warehouses
    :param cr: Database cursor
    """
    cr.execute("""select id from stock_warehouse order by id asc""")
    for res in cr.fetchall():
        _migrate_stock_warehouse(cr, res[0])


def migrate_stock_warehouse_orderpoint(cr):
    """procurement_id to procurement_ids
    :param cr: database cursor
    """
    if not openupgrade.column_exists(
            cr,
            'stock_warehouse_orderpoint',
            openupgrade.get_legacy_name('procurement_id')):
        # in this case, there was no migration for the procurement module
        # which can be okay if procurement was not installed in the 7.0 db
        return
    registry = RegistryManager.get(cr.dbname)
    openupgrade.m2o_to_x2m(
        cr, registry['stock.warehouse.orderpoint'],
        'stock_warehouse_orderpoint',
        'procurement_ids',
        openupgrade.get_legacy_name('procurement_id'))
    # Migrate move amounts to proper values
    Q = '''SELECT o.id,
                  o.%(product_uom)s move_uom,
                  o.product_min_qty,
                  o.product_max_qty,
                  o.qty_multiple,
                  t.name,
                  t.uom_id uom
           FROM stock_warehouse_orderpoint o
           LEFT JOIN product_product p ON o.product_id = p.id
           LEFT JOIN product_template t ON p.product_tmpl_id = t.id
           WHERE t.uom_id != o.%(product_uom)s
        ''' % {'product_uom': openupgrade.get_legacy_name('product_uom')}
    cr.execute(Q)
    if cr.rowcount == 0:
        return
    logger.warn("""Migrating %d stock orderpoint items""", cr.rowcount)
    orderpoints = cr.dictfetchall()
    # Gather uom data and store it in local caches for later conversions
    cr.execute('''SELECT * from product_uom''')
    uom_data = {}
    for uom in cr.dictfetchall():
        uom_data[uom['id']] = uom
    # Migrate data
    for op in orderpoints:
        p_uom_id = op['uom']
        m_uom_id = op['move_uom']
        # Check whether uom's are in the same category
        assert uom_data[p_uom_id]['category_id'] == uom_data[m_uom_id]['category_id']
        factor = 1.0 / uom_data[m_uom_id]['factor'] * uom_data[p_uom_id]['factor']
        _min = op['product_min_qty'] * factor
        _max = op['product_max_qty'] * factor
        _mul = op['qty_multiple'] * factor
        logger.warn("""Converting move qty data from %s to %s, factor: %s""",
                    uom_data[m_uom_id]['name'],
                    uom_data[p_uom_id]['name'],
                    factor)
        Q = '''UPDATE stock_warehouse_orderpoint SET
                product_min_qty = %s,
                product_max_qty = %s,
                qty_multiple = %s
               WHERE id = %s'''
        cr.execute(Q, (_min, _max, _mul, op['id']))
        assert cr.rowcount == 1


def migrate_product_supply_method(cr):
    """Procurements of products: change the supply_method for the matching route
    make to stock -> MTS Rule: by default
    make to order -> MTO Rule
    :param cr:
    """
    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    route_obj = pool['stock.location.route']
    template_obj = pool['product.template']

    mto_route_id = route_obj.search(cr, uid, [('name', 'like', 'Make To Order')])
    mto_route_id = mto_route_id and mto_route_id[0] or False

    procure_method_legacy = openupgrade.get_legacy_name('procure_method')

    if not openupgrade.column_exists(
            cr, 'product_template', procure_method_legacy):
        # in this case, there was no migration for the procurement module
        # which can be okay if procurement was not installed in the 7.0 db
        return

    if mto_route_id:
        product_ids = []
        cr.execute("SELECT id FROM product_template WHERE %s = %%s" % procure_method_legacy, ('make_to_order',))
        for res in cr.fetchall():
            product_ids.append(res[0])

        template_obj.write(cr, uid, product_ids, {'route_ids': [(6, 0, [mto_route_id])]})


def migrate_procurement_order(cr):
    """Migrates procurement orders and the new fields warehouse, move_ids, partner_dest_id
    :param cr:
    """
    pool = pooler.get_pool(cr.dbname)

    swap_procurement_move_rel(cr, pool)
    # Move Reservation to move_ids.
    registry = RegistryManager.get(cr.dbname)
    openupgrade.m2o_to_x2m(
        cr, registry['procurement.order'],
        'procurement_order', 'move_ids',
        openupgrade.get_legacy_name('move_id'))

    # Warehouse, partner from the move.
    cr.execute("""UPDATE procurement_order AS po
        SET warehouse_id = sm.warehouse_id,
        partner_dest_id = sm.partner_id
        FROM stock_move AS sm
        WHERE po.%s = sm.id""" % openupgrade.get_legacy_name('move_id'))

    # state update
    cr.execute('UPDATE procurement_order SET state = %s WHERE state = %s', ('confirmed', 'draft',))
    cr.execute('UPDATE procurement_order SET state = %s WHERE state = %s', ('running', 'ready',))
    cr.execute('UPDATE procurement_order SET state = %s WHERE state = %s', ('exception', 'waiting',))


def migrate_stock_qty(cr, pool, uid):
    """Reprocess stock moves in state done to fill stock.quant."""
    stock_move_obj = pool['stock.move']

    done_move_ids = stock_move_obj.search(cr, uid, [('state', '=', 'done')])
    stock_move_obj.write(cr, uid, done_move_ids, {'state': 'draft'})
    # Process moves using action_done.
    stock_move_obj.action_done(cr, uid, done_move_ids, context=None)


def migrate_stock_production_lot(cr):
    """Serial numbers migration
    :param cr:
    """
    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    lot_obj = pool['stock.production.lot']
    user_obj = pool['res.users']

    # Revisions to mail messages
    cr.execute("SELECT lot_id, author_id, description FROM stock_production_lot_revision")
    for lot, author, description in cr.fetchall():
        user = user_obj.browse(cr, uid, author)
        if user.email:
            lot_obj.message_post(cr, author, lot, body=description)

    # Move: prodlot_id -> Quants lot_id.
    field_name = openupgrade.get_legacy_name('prodlot_id')
    cr.execute("""select id, %s from stock_move where %s is not null""" % (field_name, field_name))
    res1 = cr.fetchall()
    for move, lot in res1:
        cr.execute("""select quant_id from stock_quant_move_rel where move_id = %s""" % (move,))
        res2 = cr.fetchall()
        for quant in res2:
            cr.execute("""UPDATE stock_quant SET lot_id = %s WHERE id = %s""" % (lot, quant[0],))
        cr.commit()


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    uid = SUPERUSER_ID

    migrate_stock_warehouse(cr)
    migrate_stock_picking(cr)
    migrate_stock_location(cr)
    migrate_stock_warehouse_orderpoint(cr)
    migrate_product_supply_method(cr)
    migrate_procurement_order(cr)
    migrate_stock_qty(cr, pool, uid)
    migrate_stock_production_lot(cr)

    # Initiate defaults before filling.
    default_spec.update({'stock.inventory': default_stock_location(cr, pool, uid)})
    openupgrade.set_defaults(cr, pool, default_spec, force=False)

    migrate_product(cr, pool)
    openupgrade.delete_model_workflow(cr, 'stock.picking')
    openupgrade_80.set_message_last_post(cr, SUPERUSER_ID, pool, ['stock.production.lot', 'stock.picking'])
