# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier, Stefan Rijnhart
#    Copyright (C) 2014 Camptocamp SA
#              (C) 2014 Therp BV
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
from openerp import pooler, SUPERUSER_ID as uid


def create_workitem_picking(cr, uid, pool):
    """
    Recover workitems missing in migration.
    :param cr: Database cursor
    :param uid: User Id
    :param pool: Database pool
    """

    pool = pooler.get_pool(cr.dbname)
    pol_obj = pool['purchase.order.line']

    # Activity
    cr.execute(
        """SELECT id FROM wkf_activity WHERE name = %s AND action = %s""",
        ('picking', 'action_picking_create()'))
    res = cr.fetchone()
    wkf_activity = res and res[0]

    # Get the not shipped moves linked to any Purchase Order
    cr.execute(
        """SELECT purchase_line_id
        FROM stock_move
        WHERE purchase_line_id is not null
        AND state != %s""",
        ('done',))
    for res in cr.fetchall():
        pol = pol_obj.browse(cr, uid, res[0])

        # Instance
        cr.execute(
            """SELECT id
            FROM wkf_instance
            WHERE res_id = %s AND res_type = %s""",
            (pol.order_id.id, 'purchase.order'))
        res3 = cr.fetchone()
        wkf_instance = res3 and res3[0]

        # Create workItem
        cr.execute(
            """SELECT id
            FROM wkf_workitem
            WHERE act_id = %s AND inst_id = %s""" % (
                wkf_activity, wkf_instance))
        res2 = cr.fetchone()
        wkf_workitem = res2 and res2[0]
        if not wkf_workitem:
            cr.execute(
                """INSERT INTO wkf_workitem (act_id, inst_id, state)
                VALUES (%s, %s, %s)""",
                (wkf_activity, wkf_instance, 'complete',))


def migrate_product_supply_method(cr):
    """
    Procurements of products: change the supply_method for the matching route
    Buy -> Buy Rule
    :param cr: Database cursor
    """
    pool = pooler.get_pool(cr.dbname)
    template_obj = pool['product.template']

    mto_route_id = pool['ir.model.data'].get_object_reference(
        cr, uid, 'purchase', 'route_warehouse0_buy')[1]

    procure_method_legacy = openupgrade.get_legacy_name('supply_method')
    if mto_route_id:
        product_ids = []
        cr.execute("""SELECT id FROM product_template WHERE %s = %%s""" % (
            procure_method_legacy), ('buy',))
        product_ids = [res[0] for res in cr.fetchall()]

        template_obj.write(
            cr, uid, product_ids, {'route_ids': [(4, mto_route_id)]})


def migrate_procurement_order(cr):
    """
    Switch the old purchase_id in Procurement Order for the new field
    Purchase Order Line
    :param cr: Database cursor
    """
    pool = pooler.get_pool(cr.dbname)
    procurement_obj = pool['procurement.order']
    purchase_legacy = openupgrade.get_legacy_name('purchase_id')
    sql_head = """SELECT id, %s FROM procurement_order""" % (purchase_legacy)
    sql_tail = """ WHERE %s is not null AND state != %%s""" % (purchase_legacy)
    cr.execute(sql_head + sql_tail, ('done',))
    res = cr.fetchall()

    for po_id, purchase_id in res:
        procurement = procurement_obj.browse(cr, uid, po_id)
        cr.execute(
            """SELECT id
            FROM purchase_order_line
            WHERE order_id = %s AND product_qty = %s AND product_id = %s""",
            (purchase_id, procurement.product_qty, procurement.product_id.id))
        res2 = cr.fetchone()
        pol_id = res2 and res2[0] or False
        if pol_id:
            procurement_obj.write(cr, uid, po_id, {'purchase_line_id': pol_id})


def migrate_stock_warehouse(cr, pool):
    """Enable purchasing on all warehouses. This will trigger the creation
    of the manufacture procurement rule"""
    warehouse_obj = pool['stock.warehouse']
    warehouse_ids = warehouse_obj.search(cr, uid, [])
    warehouse_obj.write(
        cr, uid, warehouse_ids, {'buy_to_resupply': True})
    if len(warehouse_ids) > 1:
        openupgrade.message(
            cr, 'purchase', False, False,
            "Purchasing is now enabled on all your warehouses. If this is "
            "not appropriate, disable the option 'Purchase to resupply this "
            "Warehouse' on the warehouse settings. You need to have 'Manage "
            "Push and Pull inventory flows' checked on your user record in "
            "order to access this setting.")


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    create_workitem_picking(cr, uid, pool)
    migrate_product_supply_method(cr)
    migrate_procurement_order(cr)
    migrate_stock_warehouse(cr, pool)
    openupgrade_80.set_message_last_post(cr, uid, pool, ['purchase.order'])
