from openupgradelib import openupgrade


def _rename_fields(env):
    openupgrade.rename_columns(
        env.cr,
        {
            "mailing_mailing": [
                ("contact_ab_pc", "ab_testing_pc"),
                ("unique_ab_testing", "ab_testing_enabled"),
            ],
            "mailing_trace": [
                ("sent", "sent_datetime"),
                ("opened", "open_datetime"),
                ("replied", "reply_datetime"),
                ("clicked", "links_click_datetime"),
            ],
        },
    )


def _map_mailing_mailing_reply_to_mode(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mailing_mailing
        SET reply_to_mode = CASE
            WHEN reply_to_mode = 'thread' THEN 'update'
            WHEN reply_to_mode = 'email' THEN 'new'
        END
        WHERE reply_to_mode IN ('thread', 'email')
        """,
    )


def _map_mailing_trace_failure_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mailing_trace
        SET failure_type = CASE
            WHEN failure_type = 'SMTP' THEN 'mail_smtp'
            WHEN failure_type = 'RECIPIENT' THEN 'mail_email_invalid'
            WHEN failure_type = 'BOUNCE' THEN 'mail_email_invalid'
            WHEN failure_type = 'UNKNOWN' THEN 'unknown'
        END
        WHERE failure_type IN ('SMTP', 'RECIPIENT', 'BOUNCE', 'UNKNOWN')
        """,
    )


def _map_mailing_trace_trace_status(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mailing_trace
        ADD COLUMN IF NOT EXISTS trace_status varchar
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mailing_trace
        SET trace_status = CASE
            WHEN state = 'outgoing' THEN 'outgoing'
            WHEN state = 'exception' THEN 'error'
            WHEN state = 'sent' THEN 'sent'
            WHEN state = 'opened' THEN 'open'
            WHEN state = 'replied' THEN 'reply'
            WHEN state = 'bounced' THEN 'bounce'
            WHEN state = 'ignored' THEN 'cancel'
        END
        WHERE state IN ('outgoing', 'exception', 'sent', 'opened',
            'replied', 'bounced', 'ignored')""",
    )


def _fill_mailing_mailing_schedule_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE mailing_mailing
        ADD COLUMN IF NOT EXISTS schedule_type varchar
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mailing_mailing
        SET schedule_type = CASE
            WHEN  schedule_date IS NOT NULL THEN 'scheduled'
            ELSE 'now'
        END""",
    )


def _delete_invalid_records_mailing_trace(env):
    # Delete invalid data which trigger issue due to the new constraint
    # model: now required
    # res_id: now required
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mailing_trace
        WHERE model IS NULL OR res_id IS NULL
        """,
    )


def _compute_ab_testing_total_pc(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE utm_campaign
        ADD COLUMN IF NOT EXISTS ab_testing_total_pc integer
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE utm_campaign uc
        SET ab_testing_total_pc = (
            SELECT SUM(mm.ab_testing_pc)
            FROM mailing_mailing AS mm
            WHERE mm.ab_testing_enabled = True AND uc.id = mm.campaign_id
        )""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _rename_fields(env)
    _map_mailing_mailing_reply_to_mode(env)
    _map_mailing_trace_failure_type(env)
    _map_mailing_trace_trace_status(env)
    _delete_invalid_records_mailing_trace(env)
    _fill_mailing_mailing_schedule_type(env)
    _compute_ab_testing_total_pc(env)
