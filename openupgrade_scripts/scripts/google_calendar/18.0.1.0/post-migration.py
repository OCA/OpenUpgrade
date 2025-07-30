# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _fill_google_calendar_credentials_res_users_settings(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_users_settings rus
        SET google_calendar_cal_id = gc.calendar_cal_id,
            google_calendar_rtoken = gc.calendar_rtoken,
            google_calendar_sync_token = gc.calendar_sync_token,
            google_calendar_token = gc.calendar_token,
            google_calendar_token_validity = gc.calendar_token_validity,
            google_synchronization_stopped = gc.synchronization_stopped
        FROM google_calendar_credentials gc
            JOIN res_users ru ON ru.google_calendar_account_id = gc.id
        WHERE rus.user_id = ru.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_google_calendar_credentials_res_users_settings(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "google_calendar.google_calendar_not_own_token_rule",
            "google_calendar.google_calendar_own_token_rule",
            "google_calendar.google_calendar_token_system_access",
        ],
    )
