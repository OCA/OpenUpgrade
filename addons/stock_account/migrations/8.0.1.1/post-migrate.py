B1;2802;0c# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Camptocamp SA
#              (C) 2015 Therp BV
#
#    Authors: Guewen Baconnier, Stefan Rijnhart
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

from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID


def create_properties(cr, pool):
    """ Fields moved to properties (cost_method).

    Write using the ORM so the cost_method will be written as properties.
    """
    template_obj = pool['product.template']
    company_obj = pool['res.company']
    company_ids = company_obj.search(cr, SUPERUSER_ID, [])
    sql = ("SELECT id, %s FROM product_template" %
           openupgrade.get_legacy_name('cost_method'))
    cr.execute(sql)
    for template_id, cost_method in cr.fetchall():
        for company_id in company_ids:
            ctx = {'force_company': company_id}
            template_obj.write(cr, SUPERUSER_ID, [template_id],
                               {'cost_method': cost_method},
                               context=ctx)


def propagate_invoice_state(cr):
    """ Invoice state is now propagated from sale order to procurement to
    stock move and picking. We trace it back from the picking and update
    stock moves and procurements.

    First query courtesy of Ronald Portier. Postgres' explain analyse function
    showed that using subqueries are more performant than using UPDATE...FROM,
    at least in this case.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_move sm
        SET invoice_state = (
            SELECT sp.invoice_state FROM stock_picking sp
            WHERE sm.picking_id = sp.id)
        WHERE picking_id IN (
            SELECT id FROM stock_picking sp
            WHERE sm.picking_id = sp.id
            AND sm.invoice_state <> sp.invoice_state)
    """)
    openupgrade.logged_query(
        cr,
        """
        UPDATE procurement_order po
        SET invoice_state = sm.invoice_state
        FROM stock_move sm
        WHERE sm.procurement_id = po.id
    """)


def inventory_period_id(cr, pool):
    """
    Replacing the confirmation date of the inventory with the accounting
    period of the associated company.
    """
    period_obj = pool['account.period']
    inventory_obj = pool['stock.inventory']
    date_done = openupgrade.get_legacy_name('date_done')
    cr.execute(
        """
        SELECT id, company_id, {date_done}
        FROM stock_inventory
        WHERE {date_done} IS NOT NULL
        """.format(
            date_done=date_done))
    for inv_id, company_id, date in cr.fetchall():
        period_ids = period_obj.find(
            cr, SUPERUSER_ID, dt=date[:10], context={'company_id': company_id})
        inventory_obj.write(
            cr, SUPERUSER_ID, inv_id, {'period_id': period_ids[0]})
    # Drop column as a marker that this script has run
    openupgrade.drop_columns(cr, [('stock_inventory', date_done)])


@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    """
    Run upon a fresh installation because this is a new glue module between
    stock and account in Odoo 8.0.
    Check for ourselves if the migration script applies by checking for a
    specific legacy column that is migrated here and then removed.
    """
    if not openupgrade.column_exists(
            cr, 'stock_inventory',
            openupgrade.get_legacy_name('date_done')):
        return
    pool = pooler.get_pool(cr.dbname)
    inventory_period_id(cr, pool)
    create_properties(cr, pool)
    propagate_invoice_state(cr)
