from openupgradelib import openupgrade

column_creates = [
    ("calendar.event", "candidate_id", "many2one"),
    # Pre-create to prevent recompute; this will be filled in post-migration.
    ("hr_candidate", "email_from", "char"),
    ("hr_candidate", "email_normalized", "char"),
    ("hr_candidate", "partner_phone", "char"),
    ("hr_candidate", "partner_phone_sanitized", "char"),
    ("hr_candidate", "phone_sanitized", "char"),
    ("hr_candidate", "priority", "selection"),
]

_columns_copy = {
    # Save a copy of the columns
    # that were previously stored and are now related to hr.candidate.
    "hr_applicant": [
        ("name", None, None),
        ("description", None, None),
        ("partner_id", None, None),
        ("email_from", None, None),
        ("email_normalized", None, None),
        ("availability", None, None),
        ("partner_name", None, None),
        ("partner_phone", None, None),
        ("partner_phone_sanitized", None, None),
        ("partner_mobile", None, None),
        ("partner_mobile_sanitized", None, None),
        ("phone_sanitized", None, None),
        ("type_id", None, None),
        ("color", None, None),
        ("emp_id", None, None),
        ("linkedin_profile", None, None),
    ],
}


def _create_and_fill_hr_candidate(env):
    """
    Pre-create the minimal hr_candidate table
    and populate it with data from hr_applicant.
    Create a temporary column hr_applicant_id to link the two tables.
    This is done to avoid errors with NOT NULL constraints,
    since candidate_id is a required field in hr.applicant.
    """
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TABLE IF NOT EXISTS hr_candidate (
            id SERIAL PRIMARY KEY,
            tmp_hr_applicant_id INTEGER
        )
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_applicant
        ADD COLUMN IF NOT EXISTS candidate_id INTEGER REFERENCES hr_candidate(id)
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_candidate (tmp_hr_applicant_id)
        SELECT id FROM hr_applicant
        WHERE candidate_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_applicant AS ha
        SET candidate_id = hc.id
        FROM hr_candidate AS hc
        WHERE ha.id = hc.tmp_hr_applicant_id
            AND ha.candidate_id IS NULL
        """,
    )
    # remove the temporary column used to link the two tables
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_candidate DROP COLUMN tmp_hr_applicant_id
        """,
    )


def fill_calendar_event_candidate_id(env):
    """
    Set candidate_id for calendar events from hr.applicant.
    """
    env.cr.execute(
        """
        UPDATE calendar_event ce
        SET
            candidate_id = ha.candidate_id
        FROM hr_applicant ha
        WHERE ha.id = ce.applicant_id AND ce.candidate_id IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_and_fill_hr_candidate(env)
    openupgrade.copy_columns(env.cr, _columns_copy)
    openupgrade.add_columns(env, column_creates)
    fill_calendar_event_candidate_id(env)
