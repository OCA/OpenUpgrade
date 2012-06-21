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

import pooler, logging
from openupgrade import openupgrade

logger = logging.getLogger('migrate')
MODULE = 'hr_contract'

def set_contract_job_id(cr, pool):
    """
    Migrate function_id (res.partner.function) field on hr.contract
    to job_id (hr.job).
    Create jobs if necessary, taking company_id into account.
    """
    job_pool = pool.get('hr.job')
    contract_pool = pool.get('hr.contract')
    def get_or_create(name, company_id):
        ids = job_pool.search(
            cr, 1, [('name', '=', name),
                    ('company_id', '=', company_id)])
        if ids:
            return ids[0]
        return job_pool.create(
            cr, 1, {'name': name,
                    'company_id': company_id})
    # marital might already be filled by the renaming of
    # hr_contract's marital_status
    cr.execute(
        'SELECT '
        '    hr_contract.id, '
        '    openupgrade_legacy_res_partner_function.name, '
        '    resource_resource.company_id '
        'FROM '
        '    hr_contract, '
        '    hr_employee, '
        '    resource_resource, '
        '    openupgrade_legacy_res_partner_function '
        'WHERE '
        '    hr_employee.resource_id = resource_resource.id '
        '    AND hr_contract.job_id IS NULL '
        '    AND hr_contract.employee_id = hr_employee.id '
        '    AND openupgrade_legacy_function = openupgrade_legacy_res_partner_function.id')
    for row in cr.fetchall():
        contract_pool.write(
            cr, 1, row[0], 
            {'job_id': get_or_create(row[1], row[2] or False)})


def set_contract_default_type_id(cr, pool):
    default_type_ref = pool.get('ir.model.data').get_object_reference(
        cr, 1, 'hr_contract', 'hr_contract_type_emp')
    if default_type_ref:
        openupgrade.set_defaults(
            cr, pool, 
            {'hr.contract': [('type_id', default_type_ref[1])]})
    else:
        logger.warn('%s: Default contact type not found' % MODULE)
        
@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.load_data(cr, MODULE, 'migrations/6.0.1.0/data.xml')
    set_contract_job_id(cr, pool)
    set_contract_default_type_id(cr, pool)
