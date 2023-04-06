from openupgradelib import openupgrade

_model_renames = [
    ("calendar.contacts", "calendar.filters"),
]

_table_renamed = [
    ("calendar_contacts", "calendar_filters"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_sql_constraint_safely(
        env, "calendar", "calendar_contacts", "user_id_partner_id_unique"
    )
    # we delete sql constraint before table rename
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renamed)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE calendar_filters
        ADD COLUMN IF NOT EXISTS partner_checked BOOLEAN;
        UPDATE calendar_filters
        SET partner_checked = TRUE;
        """,
    )
    openupgrade.convert_field_to_html(
        env.cr, "calendar_event", "description", "description", verbose=False
    )
    openupgrade.rename_fields(
        env,
        [
            ("calendar.recurrence", "calendar_recurrence", "fr", "fri"),
            ("calendar.recurrence", "calendar_recurrence", "mo", "mon"),
            ("calendar.recurrence", "calendar_recurrence", "sa", "sat"),
            ("calendar.recurrence", "calendar_recurrence", "su", "sun"),
            ("calendar.recurrence", "calendar_recurrence", "th", "thu"),
            ("calendar.recurrence", "calendar_recurrence", "tu", "tue"),
            ("calendar.recurrence", "calendar_recurrence", "we", "wed"),
        ],
    )
    openupgrade.delete_sql_constraint_safely(
        env, "calendar", "calendar_recurrence", "month_day"
    )
    # change the value of 'weekday' in the calendar_recurrence table
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_recurrence
        SET weekday = CASE WHEN weekday = 'FR' THEN 'FRI'
                           WHEN weekday = 'MO' THEN 'MON'
                           WHEN weekday = 'SA' THEN 'SAT'
                           WHEN weekday = 'SU' THEN 'SUN'
                           WHEN weekday = 'TH' THEN 'THU'
                           WHEN weekday = 'TU' THEN 'TUE'
                           WHEN weekday = 'WE' THEN 'WED'
                           END
        WHERE weekday IN ('FR', 'MO', 'SA', 'SU', 'TH', 'TU', 'WE')""",
    )
