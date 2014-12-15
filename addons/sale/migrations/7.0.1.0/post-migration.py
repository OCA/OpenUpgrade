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
    # disabling transitions during 'sale_order' update.
    transitions = openupgrade.deactivate_workflow_transitions(cr, 'sale.order')
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
    openupgrade.reactivate_workflow_transitions(cr, transitions)

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

