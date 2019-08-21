# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def add_group_hr_contract_manager(env):
    env.ref('hr_contract.group_hr_contract_manager').users = [
        (4, x.id) for x in env.ref('hr.group_hr_manager').users
    ]


@openupgrade.migrate()
def migrate(env, version):
    add_group_hr_contract_manager(env)
    openupgrade.load_data(
        env.cr, 'hr_contract', 'migrations/12.0.1.0/noupdate_changes.xml')
