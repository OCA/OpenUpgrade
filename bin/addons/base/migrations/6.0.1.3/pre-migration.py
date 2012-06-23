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

# TODO
# Removal of modules that are deprecated
# e.g. report_analytic_line (incorporated in hr_timesheet_invoice)

import pooler
from openupgrade import openupgrade

module_namespec = [
    # This is a list of tuples (old module name, new module name)
    ('profile_association', 'association'),
    ('report_analytic_planning', 'project_planning'),
]

renames = {
    # this is a mapping per table from old column name
    # to new column name
    'ir_property': [
        ('value', 'value_reference'),
        ],
    'res_partner_address': [
        ('function', 'tmp_mgr_function'),
        ('title', 'tmp_mgr_title'),
        ],
    'res_partner': [
        ('title', 'tmp_mgr_title'),
        ],
    'wkf_transition': [
        ('role_id', 'tmp_mgr_role_id'),
        ],
    }

renamed_xmlids = [
    ('sale.group_sale_manager', 'base.group_sale_manager'),
    ('sale.group_sale_user', 'base.group_sale_salesman'),
]

def mgr_ir_model_fields(cr):
    cr.execute('ALTER TABLE ir_model_fields ADD COLUMN selectable BOOLEAN')
    cr.execute('UPDATE ir_model_fields SET selectable = FALSE')

def mgr_company_id(cr):
    # These models add a new field for company_id, to be filled
    # by the post.py script
    # Otherwise, the osv would create it and call the _defaults function,
    # using a model that is not instanciated at that point
    # (multi_company_default).
    for table in (
        'ir_attachment', 'res_currency', 
        'res_partner_address', 'res_partner',
        'ir_sequence',
        ):
        # passing table name as a cursor param is not supported,
        # using direct python substitution
        cr.execute('ALTER TABLE "%s" ADD COLUMN company_id INTEGER' % table)

def mgr_fix_test_results(cr):
    cr.execute("UPDATE res_currency_rate SET rate = 59.9739 " +
               "FROM ir_model_data " + 
               "WHERE ir_model_data.res_id = res_currency_rate.id " +
               "AND ir_model_data.module = 'base' " +
               "AND ir_model_data.model = 'res.currency.rate' " +
               "AND ir_model_data.name = 'rateINR'")
    if not cr.rowcount:
        raise osv.except_osv("Migration: error setting INR rate in demo data, no row found", "")

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.update_module_names(
        cr, module_namespec
        )
    openupgrade.rename_columns(cr, renames)
    openupgrade.rename_xmlids(cr, renamed_xmlids)
    mgr_ir_model_fields(cr)
    mgr_company_id(cr)
    mgr_fix_test_results(cr)
    openupgrade.rename_tables(
        cr, [('res_partner_function',
              'openupgrade_legacy_res_partner_function')])
