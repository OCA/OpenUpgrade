# -*- coding: utf-8 -*-

from openerp.openupgrade import openupgrade

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(cr, [('hr_employee_marital_status', 'openupgrade_legacy_hr_employee_marital_status')])
    openupgrade.rename_columns(cr, 
            {
                'hr_employee': 
                [
                    ('marital', 'openupgrade_legacy_marital'), 
                ],
                'hr_job': 
                [
                    ('expected_employees', 'openupgrade_legacy_expected_employees')
                ],
            })
