# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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

def purge_resource_ref(cr):
    """ 
    Workaround for https://bugs.launchpad.net/openobject-addons/+bug/769632
    when the administrator user has been removed
    """
    cr.execute("""
            SELECT COUNT(id) FROM ir_model_data
            WHERE module = 'hr'
            AND name = 'employee'"""
               )
    if not cr.fetchone()[0]:
        openupgrade.logged_query(
            cr, """
            DELETE FROM ir_model_data
            WHERE module = 'hr'
            AND name = 'employee_resource_resource'"""
            )

@openupgrade.migrate()
def migrate(cr, version):
    purge_resource_ref(cr)
    openupgrade.rename_columns(cr, {
            # many2many table square dance
            'employee_category_rel': [
                ('emp_id', 'emp_id_tmp'),
                ('category_id', 'emp_id'),
                ('emp_id_tmp', 'category_id'),
                ],
            })
    openupgrade.rename_tables(cr, [('hr_employee_marital_status', openupgrade.get_legacy_name('hr_employee_marital_status'))])
    openupgrade.rename_columns(cr, 
            {
                'hr_employee': 
                [
                    ('marital', openupgrade.get_legacy_name('marital')), 
                ],
                'hr_job': 
                [
                    ('expected_employees', openupgrade.get_legacy_name('expected_employees'))
                ],
            })
