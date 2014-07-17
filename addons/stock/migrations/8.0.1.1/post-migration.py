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
from openerp import pooler, SUPERUSER_ID

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

def migrate_procure_method(cr, pool):
    """Migrate from the legacy variants from procurement.order to
    procurement.rule:
    procure_method"""

    proc_rule_obj = pool['procurement.rule']
    procure_method_name = openupgrade.get_legacy_name('procure_method')
    sql = """SELECT rule_id, {} FROM procurement_order
    """.format(procure_method_name)
    cr.execute(sql)
    rows = cr.fetchall()
    for rule_id, proc_method in rows:
        proc_rule_obj.write(cr, SUPERUSER_ID, rule_id, {'procure_method': proc_method})

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
    print "!!!! openupgrade_legacy_8_0_move_id exists: ", openupgrade.column_exists(cr, 'procurement_order', 'openupgrade_legacy_8_0_move_id')
    move_legacy = openupgrade.get_legacy_name('move_id')
    print "!!!! move_legacy exists: ", openupgrade.column_exists(cr, 'procurement_order', move_legacy)
    stock_move_obj = pool['stock.move']
    sql = """SELECT id, {} FROM {}
    """.format(move_legacy, 'procurement_order')
    cr.execute(sql)
    proc_order_rows = cr.fetchall()
    for move_id, proc_order_id in proc_order_rows:
        stock_move_obj.write(cr, uid, move_id, {'procurement_id': proc_order_id})

def migrate_procurement_sequences(cr, pool):
    pass

# TODO
# Migrate the following:
# ('procurement.sequence_mrp_op',
#      'stock.sequence_mrp_op'),
#     ('procurement.sequence_mrp_op_type',
#      'stock.sequence_mrp_op_type'),

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


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    uid = SUPERUSER_ID

    # Initiate defaults before filling.
    default_spec.update({'stock.inventory': default_stock_location(cr, pool, uid)})
    openupgrade.set_defaults(cr, pool, default_spec, force=False)

    migrate_procure_method(cr, pool)
    migrate_product(cr, pool)
    openupgrade.m2o_to_x2m(
        cr, pool['stock.warehouse.orderpoint'],
        'stock_warehouse_orderpoint', 'procurement_ids',
        openupgrade.get_legacy_name('procurement_id'))
    swap_procurement_move_rel(cr, pool)
#     procurement_obj = pool['procurement.order']
    openupgrade_80.set_message_last_post(cr, SUPERUSER_ID, pool
                                        ['stock.production.lot'])
