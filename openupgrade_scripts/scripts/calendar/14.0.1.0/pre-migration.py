# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fix_empty_end_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event
        SET end_type = 'count'
        WHERE end_type is NULL AND recurrency is True
        """,
    )


def fix_negative_interval(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event
        SET interval = 1
        WHERE interval<=0 AND recurrency is True
        """,
    )


def fix_negative_count(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event
        SET count = 1
        WHERE count<=0 AND recurrency is True
        """,
    )


def delete_empty_event_id_partner_id_records(env):
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM calendar_attendee
        WHERE event_id is null OR partner_id is null
        """,
    )


def fill_empty_privacy_and_show_as_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event
        SET privacy = 'public'
        WHERE privacy is null
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event
        SET show_as = 'busy'
        WHERE show_as is null
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fix_empty_end_type(env)
    fix_negative_interval(env)
    fix_negative_count(env)
    delete_empty_event_id_partner_id_records(env)
    fill_empty_privacy_and_show_as_fields(env)
    openupgrade.copy_columns(env.cr, {"calendar_event": [("byday", None, None)]})
