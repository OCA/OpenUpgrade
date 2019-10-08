# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_hr_expense_state(env):
    """Put 'approved' state for the records that match the condition."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense he SET state='approved'
        FROM hr_expense_sheet hes
        WHERE hes.id = he.sheet_id
            AND hes.state = 'approve' OR hes.state = 'post'""",
    )


@openupgrade.migrate()
def migrate(env, version):
    update_hr_expense_state(env)
    openupgrade.load_data(
        env.cr, 'hr_expense', 'migrations/12.0.2.0/noupdate_changes.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'hr_expense.mt_department_expense_confirmed',
            'hr_expense.mt_expense_confirmed',
        ],
    )
