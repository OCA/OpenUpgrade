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
import logging
from openerp.openupgrade import openupgrade, openupgrade_80
from openerp import pooler, SUPERUSER_ID as uid

logger = logging.getLogger('OpenUpgrade.purchase')


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
    Purchase Order Line. Search by move_dest_id first, then by product_id.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE procurement_order proc
        SET purchase_line_id = pol.id
        FROM purchase_order_line pol
        WHERE proc.{purchase_id} = pol.order_id
             AND pol.{move_dest_id} IS NOT NULL
             AND pol.{move_dest_id} = proc.{move_id}
        """.format(
            purchase_id=openupgrade.get_legacy_name('purchase_id'),
            move_dest_id=openupgrade.get_legacy_name('move_dest_id'),
            move_id=openupgrade.get_legacy_name('move_id')))

    openupgrade.logged_query(
        cr,
        """
        UPDATE procurement_order proc
        SET purchase_line_id = pol.id
        FROM purchase_order_line pol
        WHERE proc.{purchase_id} = pol.order_id
             AND proc.purchase_line_id IS NULL
             AND pol.product_id = proc.product_id
             AND pol.id NOT IN (
                 SELECT purchase_line_id
                 FROM procurement_order
                 WHERE purchase_line_id IS NOT NULL)
        """.format(
            purchase_id=openupgrade.get_legacy_name('purchase_id')))

    # Warn about dangling procurements
    cr.execute(
        """
        SELECT count(*) FROM procurement_order
        WHERE purchase_line_id IS NULL
            AND {purchase_id} IS NOT NULL
            AND state NOT IN ('done', 'exception')
        """.format(
            purchase_id=openupgrade.get_legacy_name('purchase_id')))
    count = cr.fetchone()[0]
    if count:
        logger.warning(
            "Failed to match the purchase order line for %s running "
            "procurements.", count)

    # Populate the moves generated from purchase procurements (the move_ids
    # field on the procurement order)
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_move sm
        SET procurement_id = proc.id
        FROM procurement_order proc
        WHERE proc.purchase_line_id = sm.purchase_line_id
            AND sm.purchase_line_id IS NOT NULL
        """)


def migrate_stock_warehouse(cr, pool):
    """Enable purchasing on all warehouses. This will trigger the creation
    of the purchase procurement rule"""
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
