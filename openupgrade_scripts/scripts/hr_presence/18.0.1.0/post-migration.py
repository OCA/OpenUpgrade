# Copyright 2026 OpenUpgrade Contributors
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("hr_presence_state_display"),
        "hr_presence_state_display",
        [("to_define", "out_of_working_hour")],
        table="hr_employee",
    )
