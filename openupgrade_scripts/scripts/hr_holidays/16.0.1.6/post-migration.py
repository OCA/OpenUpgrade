# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _set_allocation_validation_type(env):
    """Convert the previous `set` value to `officer` as it's mostly the same. The only
    difference is that previously if set is selected, the responsible could be empty,
    and thus the own user was selected as approver - which was incorrect -.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE hr_leave_type
        SET allocation_validation_type = 'officer'
        WHERE allocation_validation_type = 'set'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _set_allocation_validation_type(env)
    openupgrade.load_data(env.cr, "hr_holidays", "16.0.1.6/noupdate_changes.xml")
