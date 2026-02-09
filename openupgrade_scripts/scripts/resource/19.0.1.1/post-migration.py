# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def resource_calendar_flexible_hours(env):
    """
    In v19, flexible_hours is computed from schedule_type which didn't exist in v18,
    so we set schedule_type according to flexible_hours
    """
    env.cr.execute(
        "UPDATE resource_calendar SET schedule_type='flexible' WHERE flexible_hours"
    )


@openupgrade.migrate()
def migrate(env, version):
    resource_calendar_flexible_hours(env)
