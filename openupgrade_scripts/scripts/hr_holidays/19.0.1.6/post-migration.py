# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_holidays", "19.0.1.6/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "hr_holidays",
        [
            "mail_act_leave_allocation_approval",
            "mail_act_leave_allocation_second_approval",
            "mail_act_leave_approval",
            "mail_act_leave_second_approval",
        ],
        ["summary"],
    )
