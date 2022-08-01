# Copyright 2022 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_column_renames = {
    "event_event_ticket": [
        ("start_sale_date", None),
        ("end_sale_date", None),
    ],
}

_field_renames = [("event.mail", "event_mail", "done", "mail_done")]


def fill_event_registration_active(env):
    if openupgrade.column_exists(env.cr, "event_registration", "active"):
        return
    openupgrade.add_fields(
        env,
        [
            (
                "active",
                "event.registration",
                "event_registration",
                "boolean",
                "bool",
                "event",
                True,
            )
        ],
    )


def fill_event_mail_mail_count_done(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_mail
        ADD COLUMN IF NOT EXISTS mail_count_done integer;""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_mail em
        SET mail_count_done = count_emr
        FROM (SELECT em.id, count(emr.id) as count_emr
              FROM event_mail em
              JOIN event_mail_registration emr ON emr.scheduler_id = em.id
              WHERE emr.mail_sent AND em.interval_type = 'after_sub'
              GROUP BY em.id) sub
        WHERE sub.id = em.id;""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_mail em
        SET mail_count_done = ee.seats_reserved + ee.seats_used
        FROM event_event ee
        WHERE em.interval_type != 'after_sub'
            AND em.notification_type = 'mail' AND em.template_id IS NOT NULL
            AND em.event_id = ee.id;""",
    )


def fill_event_mail_template_ref(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_mail
        ADD COLUMN IF NOT EXISTS template_ref VARCHAR;
        UPDATE event_mail
        SET template_ref = 'mail.template,' || template_id
        WHERE template_id IS NOT NULL AND notification_type = 'mail'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_type_mail
        ADD COLUMN IF NOT EXISTS template_ref VARCHAR;
        UPDATE event_type_mail
        SET template_ref = 'mail.template,' || template_id
        WHERE template_id IS NOT NULL AND notification_type = 'mail'
        """,
    )
    # case event_sms was installed:
    if openupgrade.column_exists(env.cr, "event_mail", "sms_template_id"):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE event_mail
            SET template_ref = 'sms.template,' || sms_template_id
            WHERE sms_template_id IS NOT NULL AND notification_type = 'sms'
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE event_type_mail
            SET template_ref = 'sms.template,' || sms_template_id
            WHERE sms_template_id IS NOT NULL AND notification_type = 'sms'
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.convert_field_to_html(env.cr, "event_event", "note", "note")
    fill_event_registration_active(env)
    fill_event_mail_mail_count_done(env)
    fill_event_mail_template_ref(env)
