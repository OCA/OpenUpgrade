# Copyright 2022 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def date_to_datetime_tz(env, date_field_name, datetime_field_name):
    # based in openupgrade.date_to_datetime_tz
    env.cr.execute(
        """
        SELECT distinct(ee.date_tz)
        FROM event_event_ticket eet
        JOIN event_event ee ON eet.event_id = ee.id
        WHERE ee.date_tz IS NOT NULL
        """
    )
    for (timezone,) in env.cr.fetchall():
        env.cr.execute("SET TIMEZONE=%s", (timezone,))
        values = {
            "date_field_name": date_field_name,
            "datetime_field_name": datetime_field_name,
            "timezone": timezone,
        }
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE event_event_ticket eet
            SET %(datetime_field_name)s =
                eet.%(date_field_name)s::TIMESTAMP AT TIME ZONE 'UTC'
            FROM event_event ee
            WHERE eet.%(date_field_name)s IS NOT NULL
                AND eet.event_id = ee.id
                AND ee.date_tz='%(timezone)s';
            """
            % values,
        )
    env.cr.execute("RESET TIMEZONE")


def fill_event_event_ticket_datetime_fields(env):
    date_to_datetime_tz(
        env, openupgrade.get_legacy_name("start_sale_date"), "start_sale_datetime"
    )
    date_to_datetime_tz(
        env, openupgrade.get_legacy_name("end_sale_date"), "end_sale_datetime"
    )


def fill_event_type_note(env):
    # only if all events linked to that event type have the same note
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            SELECT ee.event_type_id, ee.note
            FROM event_event ee
            WHERE ee.event_type_id IS NOT NULL
            GROUP BY ee.event_type_id, ee.note
        ), sub2 AS (
            SELECT event_type_id, count(*) AS count_notes
            FROM sub
            GROUP BY event_type_id
        )
        UPDATE event_type et
        SET note = sub.note
        FROM sub
        JOIN sub2 ON (sub.event_type_id = sub2.event_type_id
            AND sub2.count_notes = 1)
        WHERE sub.event_type_id = et.id AND sub.note IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_event_event_ticket_datetime_fields(env)
    fill_event_type_note(env)
    openupgrade.load_data(env.cr, "event", "15.0.1.6/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "event",
        [
            "event_registration_mail_template_badge",
            "event_reminder",
            "event_subscription",
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_model_data
        WHERE module = 'event' AND name = 'paperformat_euro_lowmargin'
        """,
    )
