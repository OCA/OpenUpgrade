# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _merge_employee_contact(env):
    """
    Performing merge 'address_home_id' into 'work_contact_id'
    """
    partner_merge_wizard = env["base.partner.merge.automatic.wizard"]
    partner = env["res.partner"]
    env.cr.execute(
        """
        SELECT address_home_id, work_contact_id
        FROM hr_employee
        """
    )
    for address_home_id, work_contact_id in env.cr.fetchall():
        partner_merge_wizard._merge(
            [address_home_id, work_contact_id], partner.browse(work_contact_id)
        )


@openupgrade.migrate()
def migrate(env, version):
    _merge_employee_contact(env)
