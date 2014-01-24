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

def migrate_sale_order_addresses(cr, pool):
    # getting object from 'sale_stock' module because the pre-migration script
    # has renamed xml_id from 'sale' to 'sale_stock' previously
    data_obj = pool.get("ir.model.data")
    trans_1 = data_obj.read(cr, SUPERUSER_ID, 
        [data_obj._get_id(cr, SUPERUSER_ID, 'sale_stock', 'trans_ship_ship_except')], 
        ['res_id'])[0]['res_id']
    trans_2 = data_obj.read(cr, SUPERUSER_ID, 
        [data_obj._get_id(cr, SUPERUSER_ID, 'sale_stock', 'trans_ship_ship_end')], 
        ['res_id'])[0]['res_id']
    # backup values
    cr.execute("""SELECT condition FROM wkf_transition WHERE id=%s""" %(trans_1))
    value_1 = cr.fetchone()[0]
    cr.execute('SELECT condition FROM wkf_transition WHERE id=%s' %(trans_2))
    value_2 = cr.fetchone()[0]

    # disabling two transitions during 'sale_order' update.
    cr.execute("""UPDATE wkf_transition SET condition = 'False' WHERE id=%s or id=%s """ 
        %(trans_1, trans_2))
    
    # partner_address become partner
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'sale.order',
        'partner_invoice_id', openupgrade.get_legacy_name('partner_invoice_id'))
    # partner_address become partner
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'sale.order',
        'partner_shipping_id', openupgrade.get_legacy_name('partner_shipping_id'))
    # order_id (partner_address) takes precedence over partner_id (partner)
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'sale.order',
        'partner_id', openupgrade.get_legacy_name('partner_order_id'))

    # Rewriting good values
    cr.execute("""update wkf_transition set condition = %s where id=%s""",
        (value_1, trans_1))
    cr.execute("""update wkf_transition set condition = %s where id=%s""",
        (value_2, trans_2))

def migrate_sale_order_line_addresses(cr, pool):
    # partner_address become partner
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'sale.order.line',
        'address_allotment_id', openupgrade.get_legacy_name('address_allotment_id'))

def migrate_sale_order_line_names(cr, pool):
    """
    Join existing char values and obsolete notes values into
    new text field name on the sale order line.
    """
    sale_order_line_obj = pool.get('sale.order.line')
    cr.execute("""
        SELECT id, {0}, {1}
        FROM sale_order_line
        WHERE {1} is not NULL AND {1} != ''
        """.format(
            'name',
            openupgrade.get_legacy_name('notes')))
    for (sale_order_line_id, name, notes) in cr.fetchall():
        name = name + '\n' if name else ''
        sale_order_line_obj.write(
            cr, SUPERUSER_ID, [sale_order_line_id],
            {'name': name + notes})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_sale_order_addresses(cr, pool)
    migrate_sale_order_line_addresses(cr, pool)
    migrate_sale_order_line_names(cr, pool)

