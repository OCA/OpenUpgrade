from openupgradelib import openupgrade


def _move_credentials_from_res_users_to_google_calendar_credentials(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH google_calendar_credentials_tmp AS (
              INSERT INTO google_calendar_credentials (
                  calendar_rtoken, calendar_token, calendar_token_validity,
                  calendar_sync_token, calendar_cal_id, synchronization_stopped)
              SELECT DISTINCT u.google_calendar_rtoken, u.google_calendar_token,
                  u.google_calendar_token_validity, u.google_calendar_sync_token,
                  u.google_calendar_cal_id, FALSE
              FROM res_users u
              WHERE u.google_calendar_token IS NOT NULL
              RETURNING id, calendar_token
        )
        UPDATE res_users u
        SET google_cal_account_id = tmp.id
        FROM google_calendar_credentials_tmp as tmp
        WHERE tmp.calendar_token = u.google_calendar_token
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _move_credentials_from_res_users_to_google_calendar_credentials(env)
