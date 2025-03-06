# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _reset_calendar_attendance_sequence(env):
    """As the field `sequence` exists previously in 16, and you were able to change it
    on screen, there's a chance that your DB have some sequence values that alters the
    previous order when migrating.

    Thus, the safest thing is to reset the sequence value to its default value for
    preserving always the previous order.
    """
    openupgrade.logged_query(
        env.cr, "UPDATE resource_calendar_attendance SET sequence = 10"
    )


@openupgrade.migrate()
def migrate(env, version):
    _reset_calendar_attendance_sequence(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "resource",
        [
            "resource_calendar_std",
        ],
        True,
    )
