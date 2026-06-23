# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_copy_columns = {
    "event_event": [
        ("badge_format", None, None),
    ]
}

_added_fields = [
    ("event_url", "event.event", "event_event", "char", None, "event"),
    ("is_default", "event.question", "event_question", "boolean", None, "event", False),
    (
        "is_reusable",
        "event.question",
        "event_question",
        "boolean",
        None,
        "event",
        False,
    ),
]


def event_event_badge_format(env):
    """
    Remap badge printer formats to four_per_sheet
    """
    openupgrade.map_values(
        env.cr,
        "badge_format",
        "badge_format",
        [("96x134", "four_per_sheet"), ("96x82", "four_per_sheet")],
        table="event_event",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _copy_columns)
    openupgrade.add_fields(env, _added_fields)
    event_event_badge_format(env)
