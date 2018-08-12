# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2014 Priit Laes, Povi Software LLC
#           (C) 2014 Onestein BV
#           (C) 2014 Therp BV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
from psycopg2.extensions import AsIs
from openerp.openupgrade import openupgrade, openupgrade_80
from openerp import api, pooler, SUPERUSER_ID
from datetime import datetime

logger = logging.getLogger('OpenUpgrade.mrp')


def bom_product_template(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE mrp_bom
        SET product_tmpl_id=pp.product_tmpl_id
        FROM product_product pp
        WHERE pp.id=mrp_bom.product_id
        """)
    cr.execute("ALTER TABLE mrp_bom ALTER COLUMN product_tmpl_id SET NOT NULL")


def migrate_bom_lines(cr, pool):
    cr.execute("ALTER TABLE mrp_bom DROP CONSTRAINT mrp_bom_bom_id_fkey")
    bom_line_obj = pool['mrp.bom.line']
    created_from_bom_id = openupgrade.get_legacy_name('created_from_bom_id')
    cr.execute(
        "ALTER TABLE mrp_bom_line ADD COLUMN %s INTEGER",
        (AsIs(created_from_bom_id),))

    fields = {
        'bom_id': openupgrade.get_legacy_name('bom_id'),
        'product_uos': openupgrade.get_legacy_name('product_uos'),
        'product_uos_qty': openupgrade.get_legacy_name('product_uos_qty'),
    }
    sql = \
        """
        SELECT id, %(bom_id)s, product_efficiency, product_id, product_qty,
        product_rounding, product_uom, %(product_uos)s, %(product_uos_qty)s,
        routing_id, sequence, type
        FROM mrp_bom
        WHERE %(bom_id)s is NOT NULL
        """ % fields
    cr.execute(sql)
    ids = []
    for row in cr.dictfetchall():
        bom_line_id = bom_line_obj.create(cr, SUPERUSER_ID, {
            'bom_id': row[fields['bom_id']],
            'product_efficiency': row['product_efficiency'],
            'product_id': row['product_id'],
            'product_qty': row['product_qty'],
            'product_rounding': row['product_rounding'],
            'product_uom': row['product_uom'],
            'product_uos': row[fields['product_uos']],
            'product_uos_qty': row[fields['product_uos_qty']],
            'routing_id': row['routing_id'],
            'sequence': row['sequence'],
            'type': row['type']
        })
        cr.execute(
            "UPDATE mrp_bom_line SET %s = %s WHERE id = %s",
            (AsIs(created_from_bom_id), row['id'], bom_line_id))
        ids.append(str(row['id']))
        # Transfer properties from bom to bom line
        cr.execute(
            """
            INSERT INTO mrp_bom_line_mrp_property_rel
                (mrp_bom_line_id, mrp_property_id)
                SELECT %s, bom_rel.mrp_property_id
            FROM mrp_bom_mrp_property_rel bom_rel
            WHERE bom_rel.mrp_bom_id = %s
            """, (bom_line_id, row['id']))

    if ids:
        cr.execute("DELETE FROM mrp_bom WHERE id in (%s)" % ','.join(ids))


def fix_domains(cr, pool):
    sql = """
    UPDATE ir_act_window
    SET domain = NULL
    WHERE domain = '[(''bom_id'',''='',False)]' AND res_model = 'mrp.bom'
    """
    openupgrade.logged_query(cr, sql)


def update_stock_moves(env):
    stock_move_obj = env['stock.move']
    mrp_production_obj = env['mrp.production']
    ir_property_obj = env['ir.property']
    # find all locations that are used as production location
    locations = [
        ir_property_obj.get_by_record(p)
        for p in ir_property_obj.search(
            [('name', '=', 'property_stock_production')])]
    location_ids = list(set(x.id for x in locations if x))
    for move in stock_move_obj.search(
            [('location_dest_id', 'in', location_ids)]):
        productions = mrp_production_obj.search([
            '|',
            # don't rely on many2manys with domain ignoring it on search
            ('move_lines', '=', move.id),
            ('move_lines2', '=', move.id),
        ])
        if len(productions) == 1:
            env.cr.execute(
                'UPDATE stock_move SET raw_material_production_id=%s '
                'WHERE id=%s', (productions.id, move.id))
        else:
            logger.warning("Couldn't find unique production order for %s "
                           "(candidates are %s)", move.id, productions.ids)


def update_stock_picking_name(cr, pool):
    picking_obj = pool['stock.picking']
    picking_ids = picking_obj.search(
        cr, SUPERUSER_ID, ['|', ('name', '=', False), ('name', '=', '')])
    for sp in picking_obj.browse(cr, SUPERUSER_ID, picking_ids):
        if sp.origin:
            if ':' in sp.origin:
                origin = sp.origin.split(":")[1]
            else:
                origin = sp.origin
        else:
            origin = '/'
        picking_exists = picking_obj.search(
            cr, SUPERUSER_ID, [('name', '=', origin)])
        if not picking_exists:
            cr.execute(
                "UPDATE stock_picking SET name = %s WHERE id = %s",
                (origin, sp.id))
        else:
            cr.execute(
                "UPDATE stock_picking SET name = %s WHERE id = %s",
                ('%s %s' % (origin, str(datetime.now().time())), sp.id)
            )


def migrate_product_supply_method(cr, pool):
    """Procurements of products: change the supply_method for the matching
    route produce -> Manufacture Rule
    :param cr: Database cursor
    """
    mto_route_id = pool['ir.model.data'].get_object_reference(
        cr, SUPERUSER_ID, 'mrp', 'route_warehouse0_manufacture')[1]
    cr.execute(
        "SELECT id FROM product_template WHERE {column} = %s".format(
            column=openupgrade.get_legacy_name('supply_method')), ('produce',))
    template_ids = [row[0] for row in cr.fetchall()]
    logger.debug(
        "Adding manufacture route to %s product templates", len(template_ids))
    pool['product.template'].write(
        cr, SUPERUSER_ID, template_ids, {'route_ids': [(4, mto_route_id)]})


def migrate_product(cr, pool):
    """Migrate track_production"""
    prod_tmpl_obj = pool['product.template']
    cr.execute(
        """
        SELECT product_tmpl_id
        FROM product_product
        WHERE {} IS TRUE
        """.format(
            openupgrade.get_legacy_name('track_production')))
    template_ids = [row[0] for row in cr.fetchall()]
    logger.debug(
        "Setting track_production to True for %s product templates",
        len(template_ids))
    prod_tmpl_obj.write(
        cr, SUPERUSER_ID, template_ids, {'track_incoming': True})


def migrate_stock_warehouse(cr, pool):
    """Enable manufacturing on all warehouses. This will trigger the creation
    of the manufacture procurement rule"""
    warehouse_obj = pool['stock.warehouse']
    warehouse_ids = warehouse_obj.search(cr, SUPERUSER_ID, [])
    warehouse_obj.write(
        cr, SUPERUSER_ID, warehouse_ids, {'manufacture_to_resupply': True})
    if len(warehouse_ids) > 1:
        openupgrade.message(
            cr, 'mrp', False, False,
            "Manufacturing is now enabled on all your warehouses. If this is "
            "not appropriate, disable the option 'Manufacture in this "
            "Warehouse' on the warehouse settings. You need to have 'Manage "
            "Push and Pull inventory flows' checked on your user record in "
            "order to access this setting.")


def migrate_procurement_order(cr, pool):
    """ In Odoo 8.0, stock moves generated for the procurement (moves from
    the supplier or production location to stock) are recorded on the
    procurement. For mrp procurements, gather them here.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_move sm
        SET procurement_id = proc.id
        FROM procurement_order proc
        WHERE proc.production_id = sm.production_id
        AND sm.production_id IS NOT NULL
        """)


@openupgrade.migrate()
def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        pool = pooler.get_pool(cr.dbname)
        bom_product_template(cr)
        migrate_bom_lines(cr, pool)
        fix_domains(cr, pool)
        update_stock_moves(env)
        update_stock_picking_name(cr, pool)
        migrate_product_supply_method(cr, pool)
        migrate_product(cr, pool)
        migrate_stock_warehouse(cr, pool)
        migrate_procurement_order(cr, pool)
        openupgrade_80.set_message_last_post(
            cr, SUPERUSER_ID, pool,
            ['mrp.bom', 'mrp.production', 'mrp.production.workcenter.line'])
