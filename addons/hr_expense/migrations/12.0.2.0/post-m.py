# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'hr_expense', 'migrations/12.0.2.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'hr_expense.mt_department_expense_confirmed',
            'hr_expense.mt_expense_confirmed',
            'hr_expense.cat_expense',
        ],
    )
