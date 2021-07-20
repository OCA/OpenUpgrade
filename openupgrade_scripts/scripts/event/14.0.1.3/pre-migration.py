# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [("event.type", "event_type", "default_registration_max", "seats_max")]

_field_renames_event_sale = [
    ("event.type", "event_type", "use_ticketing", "use_ticket"),
    ("event.event.ticket", "event_event_ticket", "deadline", "end_sale_date"),
    ("event.registration", "event_registration", "campaign_id", "utm_campaign_id"),
    ("event.registration", "event_registration", "medium_id", "utm_medium_id"),
    ("event.registration", "event_registration", "source_id", "utm_source_id"),
]

_xmlid_renames_event_sale = [
    (
        "event_sale.access_event_event_ticket_user",
        "event.access_event_event_ticket_user",
    ),
    (
        "event_sale.access_event_event_ticket_admin",
        "event.access_event_event_ticket_manager",
    ),
]


def rename_event_event_seats(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_event
        ADD COLUMN seats_limited boolean""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event
        SET seats_limited = CASE
            WHEN seats_availability = 'limited' THEN TRUE ELSE FALSE END""",
    )


def fast_fill_kanban_state(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_event
        ADD COLUMN kanban_state varchar""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event
        SET kanban_state = CASE
            WHEN state = 'done' THEN 'done' ELSE 'normal' END""",
    )


def avoid_default_in_event_event_stage_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_event
        ADD COLUMN stage_id integer""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    if openupgrade.table_exists(env.cr, "event_event_ticket"):
        openupgrade.rename_fields(env, _field_renames_event_sale)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames_event_sale)
    rename_event_event_seats(env)
    fast_fill_kanban_state(env)
    avoid_default_in_event_event_stage_id(env)
