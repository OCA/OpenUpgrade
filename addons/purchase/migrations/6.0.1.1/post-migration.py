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
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'purchase.order': [
        ('company_id', None),
        ],    
    }

def set_order_invoice_ids(cr, pool):
    """
    Migrate many2one to many2many
    """
    order_pool = pool.get('purchase.order')
    cr.execute('SELECT id, openupgrade_legacy_invoice_id '
               'FROM purchase_order '
               'WHERE openupgrade_legacy_invoice_id IS NOT NULL')
    for row in cr.fetchall():
        order_pool.write(
            cr, 1, row[0], {'invoice_ids': [(4, row[1])]})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(cr, pool, defaults_force, force=True)
    set_order_invoice_ids(cr, pool)
    openupgrade.load_xml(cr, 'purchase', 'migrations/6.0.1.1/data.xml')
