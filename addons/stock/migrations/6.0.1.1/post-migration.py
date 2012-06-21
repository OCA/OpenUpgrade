# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
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

import pooler
from openupgrade import openupgrade

defaults_force = {
    'stock.inventory': [('company_id', None)],
    'stock.location': [('company_id', None)],
    'stock.move': [('company_id', None)],
    'stock.picking': [('company_id', None)],
    'stock.production.lot': [('company_id', None)],
    'stock.warehouse': [('company_id', None)],
    }

def update_picking_type(cr):
    """
    Picking type 'out' is now applied instead
    of type 'delivery'
    """
    openupgrade.logged_query(
        cr, 
        """
        UPDATE stock_picking
        SET type = 'out'
        WHERE type = 'delivery'
        """)

def set_valuation_accounts(cr):
    """
    The obsolete account_id field is now split up
    in an incoming and outoing account
    """
    if openupgrade.column_exists(
        cr, 'stock_location', 'openupgrade_legacy_account_id'):
        openupgrade.logged_query(
            cr,
            """
        UPDATE stock_location
        SET valuation_in_account_id = openupgrade_legacy_account_id, 
        valuation_out_account_id = openupgrade_legacy_account_id
        """)

def set_move_date(cr):
    """ Move date records the date expected
    or picking date when done. The latter is not available
    at upgrade time, so we set it to date expected
    Note that 'date' field is the old date of creation,
    which is now replaced by displaying the history field
    'create_date' (which assumingly already contains
    appropriate values)
    """
    openupgrade.logged_query(
        cr, """
        UPDATE stock_move
        SET date = date_expected
        """)
    
@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(cr, pool, defaults)
    openupgrade.set_defaults(cr, pool, defaults_force, force=True)
    set_valuation_accounts(cr)
    set_move_date(cr)
    update_picking_type(cr)
