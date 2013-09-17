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
    notes_column = openupgrade.get_legacy_name('notes')
    cr.execute("""
        SELECT id, %s, %s
        FROM purchase_order_line
        WHERE %s is not NULL
        AND %s != ''
        """ % ('name', notes_column, notes_column, notes_column))
    for (purchase_order_line_id, name, notes) in cr.fetchall():
        purchase_order_line_obj.write(
            cr, SUPERUSER_ID, [purchase_order_line_id],
            {'name': name + '\n' + notes})

def set_purchase_order_payment_term(cr, pool): 
    """
    Set a journal_id for each purchase_order, using the script similar to 
    the function _get_journal_id, used in V7 when creating a new purchase order.
    """
    partner_obj = pool.get('res.partner')
    purchase_order_obj = pool.get('purchase.order')
    cr.execute("SELECT id, partner_id, create_uid, write_uid FROM purchase_order")
    for (purchase_order_id, partner_id, create_uid, write_uid) in cr.fetchall():
        # get the property as viewed by the partner who created / modified the purchase order.
        if write_uid : 
            uid = write_uid
        else:
            uid =create_uid
        supplier = partner_obj.browse(cr, uid, partner_id)
        purchase_order_obj.write(
            cr, SUPERUSER_ID, [purchase_order_id],
            {'payment_term_id': supplier.property_supplier_payment_term.id or False})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_purchase_order_addresses(cr, pool)
    migrate_purchase_order_line_names(cr, pool)
    set_purchase_order_payment_term(cr, pool)
