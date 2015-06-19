# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Sylvain LE GAL
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
from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade, openupgrade_70
import logging


_logger = logging.getLogger(__name__)


def migrate_purchase_order_addresses(cr, pool):
    # 'dest_address_id' is now a 'partner' object.
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'purchase.order',
        'dest_address_id', openupgrade.get_legacy_name('dest_address_id'))


def migrate_purchase_order_line_names(cr, pool):
    """
    Join existing char values and obsolete notes values into
    new text field name on the purchase order line.
    """
    purchase_order_line_obj = pool.get('purchase.order.line')
    cr.execute("""
        SELECT id, {0}, {1}
        FROM purchase_order_line
        WHERE {1} is not NULL AND {1} != ''
        """.format('name',
                   openupgrade.get_legacy_name('notes')))
    for (purchase_order_line_id, name, notes) in cr.fetchall():
        name = name + '\n' if name else ''
        purchase_order_line_obj.write(
            cr, SUPERUSER_ID, [purchase_order_line_id],
            {'name': name + notes})


def set_purchase_order_payment_term(cr, pool):
    """Set a payment_term_id for each purchase_order, using the payment term
    associated to the purchase order supplier (that it's a property field).
    """
    _logger.info("Setting payment term on purchase orders...")
    # This SQL handles the priority in searching for the proper ir_property:
    # 1. res_id and company_id set (partner value)
    # 2. res_id not set but company_id set (company value)
    # 3. res_id and company_id not set (global value)
    openupgrade.logged_query(
        cr,
        """
        UPDATE purchase_order
        SET payment_term_id = ir.value
        FROM (
            SELECT
                po.id as id,
                substring(ir_property.value_reference from 22)::integer AS
                    value
            FROM ir_property, purchase_order po
            WHERE
                ir_property.name = 'property_supplier_payment_term' AND
                (ir_property.company_id = po.company_id OR
                 ir_property.company_id IS NULL) AND
                (ir_property.res_id = 'res.partner,' || po.partner_id::text OR
                 ir_property.res_id IS NULL)
            ORDER BY ir_property.res_id, ir_property.company_id NULLS LAST
        ) AS ir
        WHERE
            ir.id = purchase_order.id;
        """)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_purchase_order_addresses(cr, pool)
    set_purchase_order_payment_term(cr, pool)
    migrate_purchase_order_line_names(cr, pool)
