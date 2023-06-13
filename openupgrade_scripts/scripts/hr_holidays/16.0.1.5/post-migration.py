# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_allocation_validation_type(env):
    """Operate like the _compute_allocation_validation_type() function.

    It set "no" by default except if employee_request is set to "no"
    where it set "officer".
    """
    openupgrade.logged_query(
        env.cr, "UPDATE hr_leave_type SET allocation_validation_type = 'no'"
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE hr_leave_type
        SET allocation_validation_type = 'officer'
        WHERE employee_requests = 'no'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    set_allocation_validation_type(env)
    openupgrade.load_data(env.cr, "hr_holidays", "16.0.1.5/noupdate_changes.xml")
