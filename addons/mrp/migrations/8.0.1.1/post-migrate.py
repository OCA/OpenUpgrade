# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Priit Laes, Povi Software LLC
#         Onestein BV
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
from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID
from datetime import datetime

column_renames = {
    'mrp_bom_mrp_property_rel': [
        ('bom_id', 'mrp_bom_id'),
        ('property_id', 'mrp_property_id')
    ]
}


def move_fields(cr, pool):
    execute = openupgrade.logged_query
    queries = [
        """
UPDATE mrp_bom
SET product_tmpl_id=(SELECT product_tmpl_id
FROM product_product
WHERE product_product.id=mrp_bom.product_id)
""",
        """
ALTER TABLE mrp_bom ALTER COLUMN product_tmpl_id SET NOT NULL
""",
        """
ALTER TABLE mrp_bom DROP CONSTRAINT mrp_bom_bom_id_fkey
"""
    ]
    for sql in queries:
        execute(cr, sql)


def migrate_bom_line_property_rel(cr, uid, row, fields, new_line_id, bom_line_obj):

    """Move from bom to bom_line"""
#     cr2 = self.pool.db.cursor()
    bom_property_rel = []
    # Get the property_ids related to this row
    sql = """SELECT property_id FROM mrp_bom_property_rel WHERE bom_id = {}""".format(row['id'])

    cr.execute(sql)
    for rel_row in cr.dictfetchall():
        # fill temporary m2m bom_property_rel list
        bom_property_rel.append({'bom_id': new_line_id, 'property_id': rel_row['property_id']})

    # remove old mrp_bom_property_rel ?

    # fill new bom to property m2m table
    for values in bom_property_rel:
        bom_line_obj.write(cr, uid, values['bom_id'], {'property_id': [(4, values['property_id'])]})


# TODO check if mrp_bom property_ids needs migration
def migrate_bom_property_rel(cr, pool, uid):
    """Copy mrp_bom_property_rel to mrp_bom_mrp_property_rel
    """
    # Warning: assuming mrp_bom ids did not change!
    # Try openupgrade.rename_tables(cr, table_spec) instead (pre-script)
    pass


def migrate_bom_lines(cr, pool, uid):
    bom_line_obj = pool['mrp.bom.line']
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
        bom_line_obj.create(cr, SUPERUSER_ID, {
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
        ids.append(str(row['id']))

#         migrate_bom_line_property_rel(cr, uid, row, fields, new_line_id, bom_line_obj)

        # attribute_value_ids - new in 8.0
        # TODO: property_ids
    # Remove unneeded items
    if ids:
        cr.execute("DELETE FROM mrp_bom WHERE id in (%s)" % ','.join(ids))


def fix_domains(cr, pool, uid):
    sql = """UPDATE ir_act_window SET domain = NULL WHERE domain =
'[(''bom_id'',''='',False)]' AND res_model = 'mrp.bom'"""
    cr.execute(sql)
    cr.commit()


def update_stock_moves(cr, pool, uid):
    stock_move_obj = pool['stock.move']
    sm_ids = stock_move_obj.search(cr, uid, [])
    mrp_production_obj = pool['mrp.production']
    location_obj = pool['stock.location']
    location_id = location_obj.search(cr, uid, [('name', '=', 'Production')])
    for sm in stock_move_obj.browse(cr, uid, sm_ids):
        if 'MO' in sm.name and sm.location_dest_id.id == location_id[0]:
            prod_id = mrp_production_obj.search(cr, uid, [('name', '=', sm.name)])
            sql = """UPDATE stock_move SET raw_material_production_id = %s WHERE id = % s""" % (prod_id[0], sm.id)
            cr.execute(sql)
            cr.commit()
#             sm.write(cr, uid, {'raw_material_production_id': prod_id[0]})


def update_stock_picking_name(cr, pool, uid):
    picking_obj = pool['stock.picking']
    picking_ids = picking_obj.search(cr, uid, [])
    for sp in picking_obj.browse(cr, uid, picking_ids):
        if not sp.name:
            if ':' in sp.origin:
                origin = sp.origin.split(":")[1]
            else:
                origin = sp.origin
            sql = """UPDATE stock_picking SET name = '%s' WHERE id = %s""" % (origin, sp.id)
            picking_exists = picking_obj.search(cr, uid, [('name', '=', origin)])
            if not picking_exists:
                cr.execute(sql)
            else:
                sql = """UPDATE stock_picking SET name = '%s' WHERE id = %s""" % (
                    origin + str(datetime.now().time()), sp.id
                )
                cr.execute(sql)


def migrate_product_supply_method(cr, pool, uid):
    '''
    Procurements of products: change the supply_method for the matching route
    produce -> Manufacture Rule
    :param cr: Database cursor
    '''
    pool = pooler.get_pool(cr.dbname)
    route_obj = pool['stock.location.route']
    template_obj = pool['product.template']

    mto_route_id = route_obj.search(cr, uid, [('name', 'like', 'Manufacture')])
    mto_route_id = mto_route_id and mto_route_id[0] or False

    supply_method_legacy = openupgrade.get_legacy_name('supply_method')
    if mto_route_id:
        product_ids = []
        cr.execute("SELECT id FROM product_template WHERE %s = %%s" % supply_method_legacy, ('produce',))
        for res in cr.fetchall():
            product_ids.append(res[0])

        template_obj.write(cr, uid, product_ids, {'route_ids': [(4, mto_route_id)]})


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    move_fields(cr, pool)
    uid = SUPERUSER_ID
    migrate_bom_lines(cr, pool, uid)
    migrate_bom_property_rel(cr, pool, uid)
    fix_domains(cr, pool, uid)
    update_stock_moves(cr, pool, uid)
    update_stock_picking_name(cr, pool, uid)
    migrate_product_supply_method(cr, pool, uid)
    openupgrade.rename_columns(cr, column_renames)
