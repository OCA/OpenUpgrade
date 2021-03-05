# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade
from psycopg2 import sql


def fill_contract_company_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_contract hc
        SET company_id = COALESCE(
            he.company_id, hj.company_id, hd.company_id, ru.company_id
        )
        FROM res_users ru
        JOIN hr_contract hc2 ON ru.id = hc2.create_uid
        LEFT JOIN hr_employee he ON hc2.employee_id = he.id
        LEFT JOIN hr_job hj ON hc2.job_id = hj.id
        LEFT JOIN hr_department hd ON hc2.department_id = hd.id
        WHERE hc.company_id IS NULL AND hc2.id = hc.id
        """
    )


def fill_employee_contract_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_employee he
        SET contract_id = sub.contract_id
        FROM (
            SELECT he.id AS employee_id, hc.id as contract_id
            FROM hr_contract hc, hr_employee he
            WHERE he.id = hc.employee_id
            LIMIT 1
        ) sub
        WHERE sub.employee_id = he.id AND he.contract_id IS NULL
        """
    )


def map_hr_contract_state(cr):
    openupgrade.logged_query(
        cr, sql.SQL(
            """UPDATE hr_contract
            SET state = 'open', kanban_state = 'blocked'
            WHERE {} = 'pending'"""
        ).format(sql.Identifier(openupgrade.get_legacy_name("state")))
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_contract_company_id(env.cr)
    fill_employee_contract_id(env)
    map_hr_contract_state(env.cr)
    openupgrade.load_data(env.cr, 'hr_contract', 'migrations/13.0.1.0/noupdate_changes.xml')
