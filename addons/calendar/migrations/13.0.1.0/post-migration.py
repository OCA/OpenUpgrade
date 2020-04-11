# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _empty_calendar_event_tz(env):
    """Make sure event tz is empty for equal behavior as in v12."""
    openupgrade.logged_query(
        env.cr,
        "UPDATE calendar_event set event_tz = NULL WHERE event_tz IS NOT NULL",
    )


@openupgrade.migrate()
def migrate(env, version):
    _empty_calendar_event_tz(env)
    openupgrade.load_data(
        env.cr, 'calendar', 'migrations/13.0.1.0/noupdate_changes.xml')
