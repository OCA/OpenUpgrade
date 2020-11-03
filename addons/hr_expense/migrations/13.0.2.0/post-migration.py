# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_hr_expense_company_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense he
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = he.create_uid AND
        he.company_id is NULL""",
    )


def fill_hr_expense_sheet_company_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense_sheet hes
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = hes.create_uid AND
        hes.company_id is NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_hr_expense_company_id(env)
    fill_hr_expense_sheet_company_id(env)
    openupgrade.load_data(
        env.cr, 'hr_expense', 'migrations/13.0.2.0/noupdate_changes.xml')
