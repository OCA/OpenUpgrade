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
    'mrp.bom': [('company_id', None)],
    'mrp.production': [('company_id', None)],
    'mrp.routing': [('company_id', None)],
    'mrp.workcenter': [('company_id', None)],
}

def create_workcenter_resources(cr, pool):
    # note: set default value for company_id 
    # on the workcenter 
    # after running this function
    workcenter_pool = pool.get('mrp.workcenter')
    resource_pool = pool.get('resource.resource')
    cr.execute("""
SELECT
    id,
    openupgrade_legacy_code,
    openupgrade_legacy_name,
    openupgrade_legacy_active
FROM
    mrp_workcenter
WHERE
    resource_id is NULL""")

    for row in cr.fetchall():
        resource_id = resource_pool.create(
            cr, 1, 
            {
             'code': row[1],
             'name': row[2],
             'active': row[3],
             'resource_type': 'material',
             })
        workcenter_pool.write(
            cr, 1, row[0], {'resource_id': resource_id})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    create_workcenter_resources(cr, pool)
