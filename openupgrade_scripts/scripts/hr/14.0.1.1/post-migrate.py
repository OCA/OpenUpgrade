# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

def fill_hr_employee_company_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_employee hr
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = hr.create_uid AND
        hr.company_id is NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_hr_employee_company_id(env)
    # Load noupdate changes
    openupgrade.load_data(env.cr, "hr", "14.0.1.1/noupdate_changes.xml")
