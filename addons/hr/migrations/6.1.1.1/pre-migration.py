# -*- coding: utf-8 -*-

from openerp.openupgrade import openupgrade

@openupgrade.migrate()
def migrate(cr, version):
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
