# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # hr.contract.type
    'hr_contract.hr_contract_type_emp',
    'hr_contract.hr_contract_type_sub',
    'hr_contract.hr_contract_type_wrkr',
]


def fill_contract_company_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_contract hc
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE ru.id = hc.create_uid AND hc.company_id IS NULL
        """
    )


def fill_employee_contract_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_employee he
        SET contract_id = hc.id
        FROM hr_contract hc
        WHERE he.id = hc.employee_id AND he.company_id = hc.company_id
        """
    )


def map_hr_contract_state(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_contract
        SET state = 'open', kanban_state = 'blocked'
        WHERE state = 'pending'
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_contract_company_id(env.cr)
    fill_employee_contract_id(env)
    map_hr_contract_state(env.cr)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'hr_contract', 'migrations/13.0.1.0/noupdate_changes.xml')
