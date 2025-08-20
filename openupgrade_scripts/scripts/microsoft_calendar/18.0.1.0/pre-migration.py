# Copyright 2025 L4 Tech S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def calendar_precompute_ms_universal_event_id(env):
    """
    Now in 18.0 the ms_universal_event_id is no longer computed from microsoft_id
    - https://github.com/odoo/odoo/blob/18.0/addons/microsoft_calendar/models/microsoft_sync.py#L411
    Now the id is defined directly from the Microsoft API call, more
    specifically field 'iCalUId'
    - https://github.com/odoo/odoo/blob/18.0/addons/microsoft_calendar/utils/microsoft_calendar.py#L159
    So, in order for past calendar events and calendar recurrence to have
    a ms_universal_event_id we must precompute by splitting
    by ':' the microsoft_id
    - https://github.com/odoo/odoo/blob/18.0/addons/microsoft_calendar/models/microsoft_sync.py#L120
    """

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_recurrence
        SET ms_universal_event_id = split_part(microsoft_id, ':', 2),
            microsoft_id = split_part(microsoft_id, ':', 1)
        WHERE microsoft_id LIKE '%:%';
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event
        SET ms_universal_event_id = split_part(microsoft_id, ':', 2),
            microsoft_id = split_part(microsoft_id, ':', 1)
        WHERE microsoft_id LIKE '%:%';
        """,
    )


def microsoft_calendar_credentials_to_res_users_settings(env):
    """
    microsoft.calendar.credentials has been deleted and now settings are
    stored in res.users.settings. For each user in microsoft.calendar.credentials
    user_ids (one2many) field we must copy into that user's res.users.settings
    (user_id, many2one) the following fields:
    * calendar_sync_token -> microsoft_calendar_sync_token
    * last_sync_date -> microsoft_last_sync_date
    * synchronization_stopped -> microsoft_synchronization_stopped
    """

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_users_settings AS rus
        SET
            microsoft_calendar_sync_token = cred.calendar_sync_token,
            microsoft_last_sync_date = cred.last_sync_date,
            microsoft_synchronization_stopped = cred.synchronization_stopped
        FROM res_users AS ru
        JOIN microsoft_calendar_credentials AS cred
            ON ru.microsoft_calendar_account_id = cred.id
        WHERE rus.user_id = ru.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(
        env,
        [
            ("calendar.event", "ms_universal_event_id", "char"),
            ("calendar.recurrence", "ms_universal_event_id", "char"),
            ("res.users.settings", "microsoft_calendar_sync_token", "char"),
            ("res.users.settings", "microsoft_last_sync_date", "datetime"),
            ("res.users.settings", "microsoft_synchronization_stopped", "boolean"),
        ],
    )

    calendar_precompute_ms_universal_event_id(env)
    microsoft_calendar_credentials_to_res_users_settings(env)
