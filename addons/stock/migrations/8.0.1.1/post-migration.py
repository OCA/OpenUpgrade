# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: ONESTEiN B.V.
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

from openerp.openupgrade import openupgrade, openupgrade_80
from openerp.modules.registry import RegistryManager
from openerp import pooler, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

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
        warehouse = pool['ir.model.data'].get_object(
                                             cr, uid, 'stock', 'warehouse0')
        result = default_spec['stock_inventory']
        result = [
                  result[0],
                  ('location_id', warehouse.lot_stock_id.id)
                  ]
        return result
    except:
        message = "Failed to get the default warehouse, using default_spec."
        openupgrade.message(
                     cr, 'stock', 'stock_inventory', 'location_id', message)
        result = default_spec['stock.inventory']
        return result

#===============================================================================
# def migrate_procure_method(cr, pool):
#     """Migrate from the legacy variants from procurement.order to
#     procurement.rule:
#     procure_method"""
#
#     proc_rule_obj = pool['procurement.rule']
#     procure_method_name = openupgrade.get_legacy_name('procure_method')
#     sql = """SELECT rule_id, {} FROM procurement_order
#     """.format(procure_method_name)
#     cr.execute(sql)
#     rows = cr.fetchall()
#     for rule_id, proc_method in rows:
#         proc_rule_obj.write(cr, SUPERUSER_ID, rule_id, {'procure_method': proc_method})
#===============================================================================



def migrate_product(cr, pool):
    """Migrate the following:
     track_incoming, track_outgoing, track_production -> track_all,
     valuation"""
    prod_tmpl_obj = pool['product.template']
    track_incoming_name = openupgrade.get_legacy_name('track_incoming')
    track_outgoing_name = openupgrade.get_legacy_name('track_outgoing')
    track_production_name = openupgrade.get_legacy_name('track_production')
    valuation_name = openupgrade.get_legacy_name('valuation')

    sql = """SELECT product_tmpl_id, {}, {}, {}, {} FROM product_product
    """.format(track_incoming_name, track_outgoing_name, track_production_name, valuation_name)
    cr.execute(sql)
    rows = cr.fetchall()
    for tmpl_id, ti, to, tp, valuation in rows:
        prod_tmpl_obj.write(cr, SUPERUSER_ID, tmpl_id, {'track_incoming': ti, 'track_outgoing': to, 'track_all': tp, 'valuation': valuation})

def swap_procurement_move_rel(cr, pool):
    """Procurement_order.move_id is swapped to stock_move.procurement_id.
    So instead of a m2o from procurement_order, it is a m2o from
    stock_move in version 8.
    """

    ### CHECK DUALITY procurement_order -> move_id

    #===============================================================================
    #     select move_id, count(move_id)
    # from procurement_order
    # group by move_id
    # having count(move_id) > 1;
    #
    #===============================================================================

    uid = SUPERUSER_ID
    stock_move_obj = pool['stock.move']

    print "!!!! openupgrade_legacy_8_0_move_id exists: ", openupgrade.column_exists(cr, 'procurement_order', 'openupgrade_legacy_8_0_move_id')
    move_legacy = openupgrade.get_legacy_name('move_id')
    print "!!!! move_legacy exists: ", openupgrade.column_exists(cr, 'procurement_order', move_legacy)
    sql = """SELECT id, {} FROM {}
    """.format(move_legacy, 'procurement_order')
    cr.execute(sql)
    proc_order_rows = cr.fetchall()
    for proc_order_id,move_id in proc_order_rows:
        stock_move_obj.write(cr, uid, move_id, {'procurement_id': proc_order_id})

def restore_move_inventory_rel(cr, pool):
    uid = SUPERUSER_ID
    simr_legacy = openupgrade.get_legacy_name('stock_inventory_move_rel')
    stock_move_obj = pool['stock.move']
    cr.execute("""
        SELECT inventory_id, move_id FROM {}
    """.format(simr_legacy))
    rows = cr.fetchall()
    for inv_id, move_id in rows:
        stock_move_obj.write(cr, uid, move_id, {'inventory_id': inv_id})

def migrate_stock_location(cr):
    '''
    Create a Push rule for each pair of locations linked
    :param cr:
    '''

    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    path_obj = pool.get('stock.location.path')
    location_obj = pool.get('stock.location')
    data_obj = pool.get('ir.model.data')
    warehouse_obj = pool['stock.warehouse']

    head_sql = 'SELECT id, %s,  %s, %s, %s, name, %s FROM stock_location '%(openupgrade.get_legacy_name('chained_location_id'),
                                                                        openupgrade.get_legacy_name('chained_auto_packing'),
                                                                        openupgrade.get_legacy_name('chained_company_id'),
                                                                        openupgrade.get_legacy_name('chained_delay'),
                                                                        openupgrade.get_legacy_name('chained_picking_type'))

    tail_sql = 'WHERE %s is not null'%(openupgrade.get_legacy_name('chained_location_id'))
    cr.execute(head_sql + tail_sql)

    for location in cr.fetchall():
        loc = location_obj.browse(cr,uid,location[1])
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
        warehouse = warehouse_obj.browse(cr,uid,vals['warehouse_id'])

        if location[6] == 'in':
            vals['picking_type_id'] = warehouse.in_type_id.id
        elif location[6] == 'out':
            vals['picking_type_id'] = warehouse.out_type_id.id
        else:
            vals['picking_type_id'] = warehouse.int_type_id.id

        path_obj.create(cr,uid,vals)

def migrate_stock_picking(cr):
    '''
    Update picking records with the correct picking_type_id and state
    :param cr:
    '''

    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)

    data_obj = pool.get('ir.model.data')
    warehouse = data_obj.get_object(cr,uid,'stock','warehouse0')

    type_legacy = openupgrade.get_legacy_name('type')
    in_id = warehouse.in_type_id.id
    out_id = warehouse.out_type_id.id
    int_id = warehouse.int_type_id.id

    # Fill picking_type_id required field
    for type,type_id in (('in',in_id),('out',out_id),('internal',int_id)):
        cr.execute('UPDATE stock_picking SET picking_type_id = %%s WHERE %s = %%s'%type_legacy,(type_id,type,))

    # state key auto -> waiting
    cr.execute('UPDATE stock_picking SET state = %s WHERE state = %s',('waiting','auto',))


def migrate_stock_warehouse(cr):
    '''
    Addapt the default Warehouse to the new Warehouse functionality. Sequences, Picking types, Rules, Paths..
    :param cr: Database cursor
    '''

    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    vals = {}

    #Required field: Skip the ORM to write the code or Attribute Error
    cr.execute("UPDATE stock_warehouse SET code = %s",('WH0',))
    cr.commit()

    data_obj = pool['ir.model.data']
    location_obj = pool['stock.location']
    warehouse_obj = pool['stock.warehouse']
    picking_type_obj = pool['stock.picking.type']
    seq_obj = pool['ir.sequence']

    warehouse = data_obj.get_object(cr, uid, 'stock', 'warehouse0')
    ## Update/Create locations
    parent_location_id = data_obj.get_object_reference(cr, uid, 'stock', 'stock_location_locations')[1]
    location_id = location_obj.search(cr, uid,[('location_id','=',parent_location_id),('usage','=','view')])

    vals['view_location_id'] = location_id[0]

    # All next sublocations should not be Active because of the default value for delivery and receptions fields
    sub_locations = [
            {'name': 'Input', 'active': warehouse.reception_steps != 'one_step', 'field': 'wh_input_stock_loc_id'},
            {'name': 'Output', 'active': warehouse.delivery_steps != 'ship_only', 'field': 'wh_output_stock_loc_id'},
            {'name': 'Quality Control', 'active': warehouse.reception_steps == 'three_steps', 'field': 'wh_qc_stock_loc_id'},
            {'name': 'Packing Zone', 'active': warehouse.delivery_steps == 'pick_pack_ship', 'field': 'wh_pack_stock_loc_id'},
    ]

    for values in sub_locations:
        location_id = location_obj.create(cr, uid, {
            'name': values['name'],
            'usage': 'internal',
            'location_id': vals['view_location_id'],
            'active': values['active'],
        })
        vals[values['field']] = location_id

    #get the actual sequences values for pickings in, out and int
    next_number_in = seq_obj.search_read(cr, uid, [('code', '=', 'stock.picking.in')], ['number_next'])
    next_number_in_n = next_number_in and next_number_in[0]['number_next'] or 0
    next_number_out = seq_obj.search_read(cr, uid, [('code', '=', 'stock.picking.out')], ['number_next'])
    next_number_out_n = next_number_out and next_number_out[0]['number_next'] or 0
    next_number_int = seq_obj.search_read(cr, uid, [('code', '=', 'stock.picking')], ['number_next'])
    next_number_int_n = next_number_int and next_number_int[0]['number_next'] or 0

    #create new sequences
    in_seq_id = seq_obj.create(cr, SUPERUSER_ID, values={'name': warehouse.name + ' Sequence in', 'prefix': 'WH' + '/IN/', 'padding': 5, 'number_next': next_number_in_n})
    out_seq_id = seq_obj.create(cr, SUPERUSER_ID, values={'name': warehouse.name + ' Sequence out', 'prefix':  'WH' + '/OUT/', 'padding': 5, 'number_next': next_number_out_n})
    int_seq_id = seq_obj.create(cr, SUPERUSER_ID, values={'name': warehouse.name + ' Sequence internal', 'prefix': 'WH' + '/INT/', 'padding': 5, 'number_next': next_number_int_n})
    pack_seq_id = seq_obj.create(cr, SUPERUSER_ID, values={'name': warehouse.name + ' Sequence packing', 'prefix': 'WH' + '/PACK/', 'padding': 5})
    pick_seq_id = seq_obj.create(cr, SUPERUSER_ID, values={'name': warehouse.name + ' Sequence picking', 'prefix': 'WH' + '/PICK/', 'padding': 5})

    #get default locations
    wh_stock_loc = warehouse.lot_stock_id
    wh_input_stock_loc = vals['wh_input_stock_loc_id']
    wh_output_stock_loc = vals['wh_output_stock_loc_id']
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
    vals['out_type_id']= out_type_id
    vals['pack_type_id'] = pack_type_id
    vals['pick_type_id'] = pick_type_id
    vals['int_type_id'] = int_type_id,

    #write picking types on WH
    warehouse_obj.write(cr,uid, [warehouse.id], vals=vals)
    warehouse.refresh()

    #update ir_model_data references
    if in_type_id and out_type_id and int_type_id:
        for name,res_id in (('picking_type_in',in_type_id),
                            ('picking_type_out',out_type_id),
                           ('picking_type_internal',int_type_id)):
             cr.execute(
            'UPDATE ir_model_data set res_id = %s where name = %s',(res_id,name,))

    #create routes and push/pull rules
    new_objects_dict = warehouse_obj.create_routes(cr, uid, warehouse.id, warehouse)
    warehouse_obj.write(cr, uid, warehouse.id, new_objects_dict)

def migrate_stock_warehouse_orderpoint(cr):
    '''
    procurement_id to procurement_ids
    :param cr: database cursor
    '''
    registry = RegistryManager.get(cr.dbname)
    openupgrade.m2o_to_x2m(
        cr, registry['stock.warehouse.orderpoint'],
        'stock_warehouse_orderpoint', 'procurement_ids',
        openupgrade.get_legacy_name('procurement_id'))

def migrate_product_supply_method(cr):
    '''
    Procurements of products: change the supply_method for the matching route
    make to stock -> MTS Rule: by default
    make to order -> MTO Rule
    :param cr:
    '''
    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    route_obj = pool['stock.location.route']
    template_obj = pool['product.template']

    mto_route_id = route_obj.search(cr, uid, [('name', 'like', 'Make To Order')])
    mto_route_id = mto_route_id and mto_route_id[0] or False

    procure_method_legacy = openupgrade.get_legacy_name('procure_method')
    if mto_route_id:
        product_ids = []
        cr.execute("SELECT id FROM product_template WHERE %s = %%s"%procure_method_legacy,('make_to_order',))
        for res in cr.fetchall():
            product_ids.append(res[0])

        template_obj.write(cr,uid, product_ids, {'route_ids': [(6,0, [mto_route_id])]})

def migrate_procurement_order_method(cr):
    '''
    Procurements method: change the supply_method for the matching route
    make to stock -> MTS Rule
    make to order -> MTO Rule
    :param cr:
    '''
    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)
    route_obj = pool['stock.location.route']
    procurement_obj = pool['procurement.order']

    # TODO: Get the mto and mts from the warehouse
    mto_route_id = route_obj.search(cr, uid, [('name', 'like', 'Make To Order')])
    mto_route_id = mto_route_id and mto_route_id[0] or False
    route = route_obj.browse(cr,uid,mto_route_id)
    mto_rule_ids = [r.id for r in route.pull_ids]

    mts_route_id = route_obj.search(cr, uid, [('name', 'like', 'Make To Stock')])
    mts_route_id = mts_route_id and mts_route_id[0] or False
    route = route_obj.browse(cr,uid,mts_route_id)
    mts_rule_ids = [r.id for r in route.pull_ids]

    procure_method_legacy = openupgrade.get_legacy_name('procure_method')
    if mto_route_id and mts_route_id:
        product_ids = []
        cr.execute("SELECT id FROM procurement_order WHERE %s = %%s"%procure_method_legacy,('make_to_order',))
        for res in cr.fetchall():
            mto_ids.append(res[0])

        cr.execute("SELECT id FROM procurement_order WHERE %s = %%s"%procure_method_legacy,('make_to_stock',))
        for res in cr.fetchall():
            mts_ids.append(res[0])

        procurement_obj.write(cr,uid, mto_ids, {'route_ids': [(6,0, [mto_route_id])], 'rule_id':mto_rule_ids[0]})
        procurement_obj.write(cr,uid, mts_ids, {'route_ids': [(6,0, [mts_route_id])], 'rule_id':mts_rule_ids[0]})

def migrate_procurement_order(cr):
    '''
    Migrates procurement orders and the new fields warehouse, move_ids, partner_dest_id
    :param cr:
    '''

    uid = SUPERUSER_ID
    pool = pooler.get_pool(cr.dbname)

    migrate_procurement_order_method(cr)

    #Reservation to move_ids
    registry = RegistryManager.get(cr.dbname)
    openupgrade.m2o_to_x2m(
        cr, registry['procurement.order'],
        'procurement_order', 'move_ids',
        openupgrade.get_legacy_name('move_id'))

    #Warehouse, partner from the move
    cr.execute("""UPDATE procurement_order AS po
            SET warehouse_id = sm.warehouse_id,
            partner_dest_id = sm.partner_id
            FROM stock_move AS sm
            WHERE po.%s = sm.id"""%openupgrade.get_legacy_name('move_id'))


def migrate_stock_qty(cr, pool, uid):
    """Reprocess stock moves in state done to fill stock.quant.
    """
    stock_move_obj = pool['stock.move']

    done_move_ids = stock_move_obj.search(cr, uid, [('state', '=', 'done')])
    stock_move_obj.write(cr, uid, done_move_ids, {'state': 'draft'})
    # Process moves using action_done.
    stock_move_obj.action_done(cr, uid, done_move_ids, context=None)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    uid = SUPERUSER_ID

    migrate_stock_warehouse(cr)
    migrate_stock_picking(cr)
    migrate_stock_location(cr)
#     migrate_stock_warehouse_orderpoint(cr)  # Commented because requires procurement_id .. error for now
    migrate_product_supply_method(cr)
    migrate_procurement_order(cr)

    # Initiate defaults before filling.
    default_spec.update({'stock.inventory': default_stock_location(cr, pool, uid)})
    openupgrade.set_defaults(cr, pool, default_spec, force=False)

    #migrate_procure_method(cr, pool)
    migrate_product(cr, pool)

    swap_procurement_move_rel(cr, pool)
    openupgrade.delete_model_workflow(cr, 'stock.picking')
    migrate_stock_qty(cr, pool, uid)
#     procurement_obj = pool['procurement.order']
    openupgrade_80.set_message_last_post(cr, SUPERUSER_ID, pool, ['stock.production.lot','stock.picking'])