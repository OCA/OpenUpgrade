# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ONESTEin B.V.
#              (C) 2014 Therp B.V.
#    Snippets from odoo/addons/stock/stock.py (C) 2014 Odoo S.A.
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
from openerp import SUPERUSER_ID as uid

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


def migrate_product(cr, registry):
    """Migrate track_incoming, track_outgoing"""
    prod_tmpl_obj = registry['product.template']
    for field in 'track_incoming', 'track_outgoing':
        cr.execute(
            """
            SELECT product_tmpl_id FROM product_product
            WHERE {} IS TRUE""".format(openupgrade.get_legacy_name(field)))
        template_ids = [row[0] for row in cr.fetchall()]
        logger.debug(
            "Setting %s to True for %s product templates",
            field, len(template_ids))
        prod_tmpl_obj.write(
            cr, uid, template_ids, {field: True})


def migrate_move_inventory(cr, registry):
    """
    Inventory's move_ids needs migration from many2many to one2many on the
    stock move's inventory_id field. Should be safe to assume that a move
    was always related to a single inventory anyway.

    Set product and filter for single product inventories.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_move sm
        SET inventory_id = rel.inventory_id
        FROM {stock_inventory_move_rel} rel
        WHERE sm.id = rel.move_id
        """.format(stock_inventory_move_rel=openupgrade.get_legacy_name(
            'stock_inventory_move_rel')))

    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_inventory si
        SET product_id = l.product_id,
            filter = 'product'
        FROM stock_inventory_line l
        WHERE l.inventory_id = si.id
            AND (SELECT COUNT(*)
                 FROM stock_inventory_line
                 WHERE inventory_id = si.id) = 1;
        """)

    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_inventory si
        SET location_id = l.location_id
        FROM stock_inventory_line l
        WHERE l.inventory_id = si.id
        """)


def migrate_stock_location(cr, registry):
    """Create a Push rule for each pair of locations linked. Will break if
    there are multiple warehouses for the same company."""
    path_obj = registry['stock.location.path']
    location_obj = registry['stock.location']
    warehouse_obj = registry['stock.warehouse']

    head_sql = """SELECT id, %s, %s, %s, %s, name, %s
        FROM stock_location""" % (
        openupgrade.get_legacy_name('chained_location_id'),
        openupgrade.get_legacy_name('chained_auto_packing'),
        openupgrade.get_legacy_name('chained_company_id'),
        openupgrade.get_legacy_name('chained_delay'),
        openupgrade.get_legacy_name('chained_picking_type'))
    tail_sql = """ WHERE %s = 'fixed'""" % (
        openupgrade.get_legacy_name('chained_location_type'))
    cr.execute(head_sql + tail_sql)

    for location in cr.fetchall():
        loc = location_obj.browse(cr, uid, location[1])
        loc_from = location_obj.browse(cr, uid, location[0])
        name = '{} -> {}'.format(location[5], loc.name)
        vals = {
            'active': True,
            'propagate': True,
            'location_from_id': location[0],
            'location_dest_id': location[1],
            'auto': location[2],
            'company_id': location[3],
            'delay': location[4],
            'name': name,
        }

        company_id = location[3] or loc.company_id.id or loc_from.company_id.id
        args = company_id and [('company_id', '=', company_id)] or []
        warehouse_ids = warehouse_obj.search(cr, uid, args)
        if not warehouse_ids:
            warehouse_ids = [registry['ir.model.data'].xmlid_to_res_id(
                cr, uid, 'stock.warehouse0', raise_if_not_found=True)]
            openupgrade.message(
                cr, 'stock', 'stock_location_path', 'warehouse_id',
                'No warehouse found for company #%s, but this company does '
                'have chained pickings. Taking the default warehouse.',
                company_id)
        vals['warehouse_id'] = warehouse_ids[0]
        warehouse = warehouse_obj.browse(cr, uid, vals['warehouse_id'])
        if len(warehouse_ids) > 1:
            openupgrade.message(
                cr, 'stock', 'stock_location_path', 'warehouse_id',
                'Multiple warehouses found for location path %s. Taking '
                '%s. Please verify this setting.', name, warehouse.name)
        if location[6] == 'in':
            vals['picking_type_id'] = warehouse.in_type_id.id
        elif location[6] == 'out':
            vals['picking_type_id'] = warehouse.out_type_id.id
        else:
            vals['picking_type_id'] = warehouse.int_type_id.id
        path_obj.create(cr, uid, vals)


def migrate_stock_picking(cr, registry):
    """Update picking records with the correct picking_type_id and state.
    As elsewhere, multiple warehouses with the same company pose a problem.
    """
    warehouse_obj = registry['stock.warehouse']
    company_obj = registry['res.company']
    picking_obj = registry['stock.picking']
    type_legacy = openupgrade.get_legacy_name('type')
    for company in company_obj.browse(
            cr, uid, company_obj.search(
                cr, uid, [])):
        warehouse_ids = warehouse_obj.search(
            cr, uid, [('company_id', '=', company.id)])
        if not warehouse_ids:
            picking_ids = picking_obj.search(
                cr, uid, [('company_id', '=', company.id)])
            if not picking_ids:
                continue
            warehouse_ids = [registry['ir.model.data'].xmlid_to_res_id(
                cr, uid, 'stock.warehouse0', raise_if_not_found=True)]
            openupgrade.message(
                cr, 'stock', 'stock_picking', 'picking_type_id',
                'No warehouse found for company %s, but this company does '
                'have pickings. Taking the default warehouse.', company.name)
        warehouse = warehouse_obj.browse(cr, uid, warehouse_ids[0])
        if len(warehouse_ids) > 1:
            openupgrade.message(
                cr, 'stock', 'stock_picking', 'picking_type_id',
                'Multiple warehouses found for company %s. Taking first'
                'one found (%s) to determine the picking types for this '
                'company\'s pickings. Please verify this setting.',
                company.name, warehouse.name)

        # Fill picking_type_id required field
        for picking_type, type_id in (
                ('in', warehouse.in_type_id.id),
                ('out', warehouse.out_type_id.id),
                ('internal', warehouse.int_type_id.id)):
            openupgrade.logged_query(
                cr,
                """
                UPDATE stock_picking SET picking_type_id = %s
                WHERE {type_legacy} = %s
                """.format(type_legacy=type_legacy),
                (type_id, picking_type,))

    # state key auto -> waiting
    cr.execute("UPDATE stock_picking SET state = %s WHERE state = %s",
               ('waiting', 'auto',))


def set_warehouse_view_location(cr, registry, warehouse):
    """
    Getting the shared view locations of all existing locations which is
    not the overall Physical locations view. Searching for parent
    left/right explicitely for lack of a parent_of operator.
    For parent left/right clarification, refer to
    https://answers.launchpad.net/openobject-server/+question/186704

    Known issue: we don't know if the found view location includes locations
    of other warehouses and is thus not warehouse specific so we'll just warn
    about the changes we make.
    """
    location_obj = registry['stock.location']
    all_warehouse_view = registry['ir.model.data'].get_object_reference(
        cr, uid, 'stock', 'stock_location_locations')[1]
    location_ids = location_obj.search(
        cr, uid,
        [('parent_left', '<', warehouse.lot_stock_id.parent_left),
         ('parent_left', '<', warehouse.lot_stock_id.parent_right),
         ('parent_right', '>', warehouse.lot_stock_id.parent_left),
         ('parent_right', '>', warehouse.lot_stock_id.parent_right),
         ('parent_left', '<', warehouse.wh_input_stock_loc_id.parent_left),
         ('parent_left', '<', warehouse.wh_input_stock_loc_id.parent_right),
         ('parent_right', '>', warehouse.wh_input_stock_loc_id.parent_left),
         ('parent_right', '>', warehouse.wh_input_stock_loc_id.parent_right),
         ('parent_left', '<', warehouse.wh_output_stock_loc_id.parent_left),
         ('parent_left', '<', warehouse.wh_output_stock_loc_id.parent_right),
         ('parent_right', '>', warehouse.wh_output_stock_loc_id.parent_left),
         ('parent_right', '>', warehouse.wh_output_stock_loc_id.parent_right),
         ('id', 'child_of', all_warehouse_view),
         ('id', '!=', all_warehouse_view),
         ])
    if location_ids:
        warehouse_view_id = location_ids[0]
        location = location_obj.browse(
            cr, uid, location_ids[0])
        openupgrade.message(
            cr, 'stock', 'stock_warehouse', 'view_location_id',
            "Selecting location '%s' as the view location of warehouse %s",
            location.name, warehouse.code)
    else:
        openupgrade.message(
            cr, 'stock', 'stock_warehouse', 'view_location_id',
            "Creating new view location for warehouse %s",
            warehouse.code)
        for location in (
                warehouse.lot_stock_id,
                warehouse.wh_input_stock_loc_id,
                warehouse.wh_output_stock_loc_id):
            if (location.location_id and
                    location.location_id.id != all_warehouse_view):
                openupgrade.message(
                    cr, 'stock', 'stock_location', 'location_id',
                    "Overwriting existing parent location (%s) of location %s "
                    "with the warehouse's new view location",
                    location.location_id.name, location.name)

        warehouse_view_id = location_obj.create(
            cr, uid, {
                'name': warehouse.code,
                'usage': 'view',
                'location_id': all_warehouse_view,
            })
        location_obj.write(
            cr, uid, set([
                warehouse.lot_stock_id.id,
                warehouse.wh_input_stock_loc_id.id,
                warehouse.wh_output_stock_loc_id.id]),
            {'location_id': warehouse_view_id})
    warehouse.write({'view_location_id': warehouse_view_id})
    warehouse.refresh()


def _migrate_stock_warehouse(cr, registry, res_id):
    """Warehouse adaptation to the new functionality. Sequences, Picking types,
    Rules.
    """
    location_obj = registry['stock.location']
    warehouse_obj = registry['stock.warehouse']
    picking_type_obj = registry['stock.picking.type']
    seq_obj = registry['ir.sequence']

    warehouse = warehouse_obj.browse(cr, uid, res_id)
    set_warehouse_view_location(cr, registry, warehouse)
    vals = {}

    # Create new locations, inactive as per default config. Changing the
    # warehouse configuration makes them active automatically.
    for name, field in [
            ('Quality Control', 'wh_qc_stock_loc_id'),
            ('Packing Zone', 'wh_pack_stock_loc_id')]:
        vals[field] = location_obj.create(
            cr, uid, {
                'name': name,
                'usage': 'internal',
                'location_id': warehouse.view_location_id.id,
                'active': False,
            })

    # Create new sequences to guarantee separate sequences per warehouse.
    # Transfer the number_next from the existing sequences.
    def get_sequence_next(code, default=1):
        sequence_ids = (
            seq_obj.search(
                cr, uid, [('company_id', '=', warehouse.company_id.id),
                          ('code', '=', code)]) or
            seq_obj.search(
                cr, uid, [('company_id', '=', False), ('code', '=', code)]))
        if not sequence_ids:
            return default
        return seq_obj.browse(cr, uid, sequence_ids[0]).number_next

    in_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence in',
        'prefix': warehouse.code + '/IN/', 'padding': 5,
        'number_next': get_sequence_next('stock.picking.in'),
    })
    out_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence out',
        'prefix': warehouse.code + '/OUT/', 'padding': 5,
        'number_next': get_sequence_next('stock.picking.out'),
    })
    int_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence internal',
        'prefix': warehouse.code + '/INT/', 'padding': 5,
        # OCB has stock.picking.internal, Odoo has stock.picking
        'number_next': get_sequence_next(
            'stock.picking', default=0) or get_sequence_next(
            'stock.picking.internal'),
    })
    pack_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence packing',
        'prefix': warehouse.code + '/PACK/', 'padding': 5
    })
    pick_seq_id = seq_obj.create(cr, uid, values={
        'name': warehouse.name + ' Sequence picking',
        'prefix': warehouse.code + '/PICK/', 'padding': 5
    })

    def get_location_by_usage(usage):
        """
        Try to find a company specific location first. The fallback query
        will always at least contain the customer or supplier location from
        the module's data file which is noupdate nowadays.
        """
        location_ids = (
            location_obj.search(
                cr, uid, [('usage', '=', usage),
                          ('company_id', '=', warehouse.company_id.id)]) or
            location_obj.search(
                cr, uid, [('usage', '=', usage),
                          ('company_id', '=', False)]))
        return location_ids[0]

    customer_loc_id = get_location_by_usage('customer')
    supplier_loc_id = get_location_by_usage('supplier')

    # - Creation of sequence adapted from stock.py -
    # Choose the next available color for the picking types of this warehouse
    color = 0
    available_colors = [c % 9 for c in range(3, 12)]
    all_used_colors = picking_type_obj.search_read(
        cr, uid, [('warehouse_id', '!=', False),
                  ('color', '!=', False)], ['color'], order='color')
    # Don't use sets to preserve the list order
    for x in all_used_colors:
        if x['color'] in available_colors:
            available_colors.remove(x['color'])
    if available_colors:
        color = available_colors[0]

    # Order the picking types with a sequence allowing to have the following
    # suit for each warehouse: reception, internal, pick, pack, ship.
    max_sequence = picking_type_obj.search_read(
        cr, uid, [], ['sequence'], order='sequence desc')
    max_sequence = max_sequence and max_sequence[0]['sequence'] or 0

    # TODO: apply max_sequence below

    in_type_id = picking_type_obj.create(
        cr, uid, {
            'name': 'Receptions',
            'warehouse_id': warehouse.id,
            'code': 'incoming',
            'sequence_id': in_seq_id,
            'default_location_src_id': supplier_loc_id,
            'default_location_dest_id': warehouse.wh_input_stock_loc_id.id,
            'sequence': max_sequence + 1,
            'color': color,
        })
    out_type_id = picking_type_obj.create(
        cr, uid, {
            'name': 'Delivery Orders',
            'warehouse_id': warehouse.id,
            'code': 'outgoing',
            'sequence_id': out_seq_id,
            'return_picking_type_id': in_type_id,
            'default_location_src_id': warehouse.wh_output_stock_loc_id.id,
            'default_location_dest_id': customer_loc_id,
            'sequence': max_sequence + 4,
            'color': color,
        })
    picking_type_obj.write(
        cr, uid, [in_type_id], {'return_picking_type_id': out_type_id})

    int_type_id = picking_type_obj.create(
        cr, uid, {
            'name': 'Internal Transfers',
            'warehouse_id': warehouse.id,
            'code': 'internal',
            'sequence_id': int_seq_id,
            'default_location_src_id': warehouse.lot_stock_id.id,
            'default_location_dest_id': warehouse.lot_stock_id.id,
            'sequence': max_sequence + 2,
            'color': color,
        })
    pack_type_id = picking_type_obj.create(
        cr, uid, {
            'name': 'Pack',
            'warehouse_id': warehouse.id,
            'code': 'internal',
            'sequence_id': pack_seq_id,
            'default_location_src_id': vals['wh_pack_stock_loc_id'],
            'default_location_dest_id': warehouse.lot_stock_id.id,
            'active': False,
            'sequence': max_sequence + 3,
            'color': color,
        })
    pick_type_id = picking_type_obj.create(
        cr, uid, {
            'name': 'Pick',
            'warehouse_id': warehouse.id,
            'code': 'internal',
            'sequence_id': pick_seq_id,
            'default_location_src_id': warehouse.lot_stock_id.id,
            'default_location_dest_id': vals['wh_pack_stock_loc_id'],
            'active': False,
            'color': color,
            'sequence': max_sequence + 2,
        })

    vals.update({
        'in_type_id': in_type_id,
        'out_type_id': out_type_id,
        'pack_type_id': pack_type_id,
        'pick_type_id': pick_type_id,
        'int_type_id': int_type_id,
    })

    # Write picking types on WH.
    warehouse.write(vals)
    warehouse.refresh()
    # create routes and push/pull rules
    warehouse.write(
        warehouse_obj.create_routes(cr, uid, [warehouse.id], warehouse))


def migrate_stock_warehouse(cr, registry):
    """Migrate all the warehouses"""
    warehouse_obj = registry['stock.warehouse']
    # Set code
    cr.execute("""select id, code from stock_warehouse order by id asc""")
    res = cr.fetchall()
    for wh in res:
        if not wh[1]:
            warehouse_obj.write(cr, uid, wh[0], {'code': 'WH%s' % (wh[0])})
    # Migrate each warehouse
    for wh in res:
        _migrate_stock_warehouse(cr, registry, wh[0])


def migrate_stock_warehouse_orderpoint(cr):
    """procurement_id to procurement_ids
    :param cr: database cursor
    """
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
    logger.warn("Migrating %d stock orderpoint items", cr.rowcount)
    orderpoints = cr.dictfetchall()
    # Gather uom data and store it in local caches for later conversions
    cr.execute('SELECT * from product_uom')
    uom_data = {}
    for uom in cr.dictfetchall():
        uom_data[uom['id']] = uom
    # Migrate data
    for op in orderpoints:
        p_uom_id = op['uom']
        m_uom_id = op['move_uom']
        # Check whether uom's are in the same category
        assert uom_data[p_uom_id]['category_id'] ==\
            uom_data[m_uom_id]['category_id']
        factor = 1.0 / uom_data[m_uom_id]['factor'] *\
            uom_data[p_uom_id]['factor']
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


def migrate_product_supply_method(cr, registry):
    """Procurements of products: change the supply_method for the matching
    route.
    make to stock -> MTS Rule: by default
    make to order -> MTO Rule
    :param cr:
    """
    route_obj = registry['stock.location.route']
    template_obj = registry['product.template']

    mto_route_id = route_obj.search(
        cr, uid, [('name', 'like', 'Make To Order')])
    mto_route_id = mto_route_id and mto_route_id[0] or False

    procure_method_legacy = openupgrade.get_legacy_name('procure_method')

    if mto_route_id:
        product_ids = []
        cr.execute("SELECT id FROM product_template WHERE %s = %%s" % (
            procure_method_legacy,), ('make_to_order',))
        for res in cr.fetchall():
            product_ids.append(res[0])

        template_obj.write(
            cr, uid, product_ids, {'route_ids': [(6, 0, [mto_route_id])]})


def migrate_procurement_order(cr, registry):
    """Set warehouse, partner from the move."""
    cr.execute(
        """
        UPDATE procurement_order AS po
        SET partner_dest_id = sm.partner_id
        FROM stock_move AS sm
        WHERE po.move_dest_id = sm.id
        """)
    company_obj = registry['res.company']
    warehouse_obj = registry['stock.warehouse']
    procurement_obj = registry['procurement.order']
    for company in company_obj.browse(
            cr, uid, company_obj.search(cr, uid, [])):
        procurement_ids = procurement_obj.search(
            cr, uid, [('company_id', '=', company.id)])
        if not procurement_ids:
            continue
        warehouse_ids = warehouse_obj.search(
            cr, uid, [('company_id', '=', company.id)])
        if not warehouse_ids:
            # Warehouse_id is not required on procurements
            openupgrade.message(
                cr, 'stock', 'procurement_order', 'warehouse_id',
                'No warehouse found for company %s, but this company does '
                'have procurements. Not setting a warehouse on them.',
                company.name)
            continue
        warehouse = warehouse_obj.browse(cr, uid, warehouse_ids[0])
        if len(warehouse_ids) > 1:
            openupgrade.message(
                cr, 'stock', 'procurement_order', 'warehouse_id',
                'Multiple warehouses found for company %s. Taking first'
                'one found (%s) to append to this company\'s procurements. '
                'Please verify this setting.',
                company.name, warehouse.name)
        procurement_obj.write(
            cr, uid, procurement_ids, {'warehouse_id': warehouse.id})


def migrate_stock_qty(cr, registry):
    """Reprocess stock moves in state done to fill stock.quant."""
    stock_move_obj = registry['stock.move']

    done_move_ids = stock_move_obj.search(cr, uid, [('state', '=', 'done')])
    openupgrade.message(
        cr, 'stock', 'stock_move', 'state',
        'Reprocess %s stock moves in state done to fill stock.quant',
        len(done_move_ids))
    stock_move_obj.write(cr, uid, done_move_ids, {'state': 'draft'})
    # Process moves using action_done.
    stock_move_obj.action_done(cr, uid, done_move_ids, context=None)


def migrate_stock_production_lot(cr, registry):
    """Serial numbers migration
    :param cr:
    """
    lot_obj = registry['stock.production.lot']
    user_obj = registry['res.users']

    # Revisions to mail messages
    cr.execute("""
        SELECT lot_id, author_id, description
        FROM stock_production_lot_revision""")
    for lot, author, description in cr.fetchall():
        user = user_obj.browse(cr, uid, author)
        if user.email:
            lot_obj.message_post(cr, author, lot, body=description)

    # Move: prodlot_id -> Quants lot_id.
    field_name = openupgrade.get_legacy_name('prodlot_id')
    cr.execute("""select id, %s from stock_move where %s is not null""" % (
        field_name, field_name))
    res1 = cr.fetchall()
    for move, lot in res1:
        cr.execute("""
            SELECT quant_id
            FROM stock_quant_move_rel
            WHERE move_id = %s""" % (move,))
        res2 = cr.fetchall()
        for quant in res2:
            cr.execute("""
                UPDATE stock_quant
                SET lot_id = %s
                WHERE id = %s""" % (lot, quant[0],))
        cr.commit()


def reset_warehouse_data_ids(cr, registry):
    """ While stock_data.yml creates some noupdate XML IDs, they contain empty
    res_ids because the main warehouse was not fully configured at that time.
    Reset them here."""
    data_model = registry['ir.model.data']
    warehouse = data_model.xmlid_to_object(
        cr, uid, 'stock.warehouse0')
    for name, res_id in (
            ('stock_location_stock', warehouse.lot_stock_id.id),
            ('stock_location_company', warehouse.wh_input_stock_loc_id.id),
            ('stock_location_output', warehouse.wh_output_stock_loc_id.id),
            ('location_pack_zone', warehouse.wh_pack_stock_loc_id.id),
            ('picking_type_internal', warehouse.int_type_id.id),
            ('picking_type_in', warehouse.in_type_id.id),
            ('picking_type_out', warehouse.out_type_id.id)):
        assert data_model.search(
            cr, uid, [('module', '=', 'stock'), ('name', '=', name)]), (
            'XML name "stock.{}" does not exist. Was stock_data.yml loaded '
            'correctly?'.format(name))
        assert res_id, (
            'New id for xml name {} is not valid. Something went wrong.'
            ''.format(name))
        cr.execute(
            """UPDATE ir_model_data SET res_id = %s
               WHERE module = 'stock' AND name = %s""",
            (res_id, name))


def create_stock_move_fields(cr, registry):
    """ This function reduce creation time of the stock_move fields
       (See pre script, for more information)
    """
    sm_obj = registry['stock.move']
    logger.info("Fast creation of the field stock_move.product_qty (post)")
    # Set product_qty = product_uom_qty if uom_id of stock move
    # is the same as uom_id of product. (Main case)
    openupgrade.logged_query(cr, """
        UPDATE stock_move sm1
        SET product_qty = product_uom_qty
        FROM
            (SELECT sm2.id from stock_move sm2
            INNER join product_product pp on sm2.product_id = pp.id
            INNER join product_template pt on pp.product_tmpl_id = pt.id
            where pt.uom_id = sm2.product_uom) as res
        WHERE sm1.id = res.id""")
    # Use ORM if uom id are different
    cr.execute(
        """SELECT sm2.id from stock_move sm2
        INNER join product_product pp on sm2.product_id = pp.id
        INNER join product_template pt on pp.product_tmpl_id = pt.id
        where pt.uom_id != sm2.product_uom""")
    sm_ids = [row[0] for row in cr.fetchall()]
    qty_vals = sm_obj._quantity_normalize(cr, uid, sm_ids, None, None)
    for id, qty in qty_vals.iteritems():
        cr.execute("UPDATE stock_move set product_qty = '%s' where id=%s" % (
            qty, id))


@openupgrade.migrate()
def migrate(cr, version):
    """
    It can be the case that procurement was not installed in the 7.0 database,
    as in 7.0 stock was a dependency of procurement and not the other way
    around like it is in 8.0. So we need to check if we are migrating a
    database in which procurement related stuff needs to be migrated.
    """
    registry = RegistryManager.get(cr.dbname)
    create_stock_move_fields(cr, registry)
    have_procurement = openupgrade.column_exists(
        cr, 'product_template', openupgrade.get_legacy_name('procure_method'))

    migrate_stock_warehouse(cr, registry)
    migrate_stock_picking(cr, registry)
    migrate_stock_location(cr, registry)

    if have_procurement:
        migrate_stock_warehouse_orderpoint(cr)
        migrate_product_supply_method(cr, registry)
        migrate_procurement_order(cr, registry)

    migrate_stock_qty(cr, registry)
    migrate_stock_production_lot(cr, registry)

    # Initiate defaults before filling.
    openupgrade.set_defaults(cr, registry, default_spec, force=False)

    migrate_product(cr, registry)
    openupgrade.delete_model_workflow(cr, 'stock.picking')
    openupgrade_80.set_message_last_post(
        cr, uid, registry, ['stock.production.lot', 'stock.picking'])
    migrate_move_inventory(cr, registry)
    reset_warehouse_data_ids(cr, registry)
