# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_added_fields = [
    (
        "schedule_end",
        "maintenance.request",
        "maintenance_request",
        "datetime",
        None,
        "maintenance",
    )
]


def fill_maintenance_request_schedule_end(env):
    """
    Fill the schedule_end field in maintenance.request records
    based on schedule_date and duration.
    If duration is not set, default to 1 hour.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE maintenance_request mr
        SET schedule_end = schedule_date + INTERVAL '1 hour' * (
            CASE
                WHEN mr.duration = 0 THEN 1
                ELSE COALESCE(mr.duration, 1)
            END
        )
        WHERE mr.schedule_date IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _added_fields)
    fill_maintenance_request_schedule_end(env)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE maintenance_equipment_category
        DROP CONSTRAINT IF EXISTS maintenance_equipment_category_alias_id_fkey;
        """,
    )
