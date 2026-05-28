from openupgradelib import openupgrade

_renamed_models = [
    ("hr.attendance.overtime", "hr.attendance.overtime.line"),
]

_renamed_tables = [
    ("hr_attendance_overtime", "hr_attendance_overtime_line"),
]

_renamed_fields = [
    ("hr.attendance", "hr_attendance", "in_city", "in_location"),
    ("hr.attendance", "hr_attendance", "out_city", "out_location"),
]

# Removed in 19.0 but noupdate, so not swept by the standard module update.
_obsolete_rule_xmlids = [
    "hr_attendance.hr_attendance_overtime_rule_employee_company",
    "hr_attendance.hr_attendance_rule_attendance_officer_overtime_restrict",
    "hr_attendance.hr_attendance_rule_attendance_overtime_admin",
    "hr_attendance.hr_attendance_rule_attendance_overtime_simple_user",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _renamed_models)
    openupgrade.rename_tables(env.cr, _renamed_tables)
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.delete_records_safely_by_xml_id(env, _obsolete_rule_xmlids)
    # Precreate the new required/computed columns for the renamed table's rows.
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_attendance_overtime_line
            ADD COLUMN IF NOT EXISTS status varchar,
            ADD COLUMN IF NOT EXISTS manual_duration double precision
        """,
    )
    openupgrade.logged_query(
        env.cr,
        "UPDATE hr_attendance_overtime_line SET status = 'approved' "
        "WHERE status IS NULL",
    )
    openupgrade.logged_query(
        env.cr,
        "UPDATE hr_attendance_overtime_line SET manual_duration = duration "
        "WHERE manual_duration IS NULL",
    )
    openupgrade.logged_query(
        env.cr,
        "UPDATE hr_attendance_overtime_line SET date = create_date::date "
        "WHERE date IS NULL",
    )
