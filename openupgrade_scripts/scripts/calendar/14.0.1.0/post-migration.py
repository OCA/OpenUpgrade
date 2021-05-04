# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_follow_recurrence_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event ce
        SET follow_recurrence = True
        WHERE recurrency = True
        """,
    )


def map_calendar_event_byday(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("byday"),
        "byday",
        [("5", "-1")],
        table="calendar_event",
    )


@openupgrade.migrate()
def migrate(env, version):
    update_follow_recurrence_field(env)
    map_calendar_event_byday(env)
    openupgrade.load_data(env.cr, "calendar", "14.0.1.0/noupdate_changes.xml")
