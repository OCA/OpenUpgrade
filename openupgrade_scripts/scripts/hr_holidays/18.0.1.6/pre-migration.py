from openupgradelib import openupgrade

_column_renames = {
    "hr_leave": [("request_hour_from", None), ("request_hour_to", None)],
    "hr_leave_allocation": [("private_name", "name")],
}

_column_adds = [
    ("hr.leave", "request_hour_from", "float"),
    ("hr.leave", "request_hour_to", "float"),
]


def refill_hr_leave_request_hours(env):
    old_request_hour_from = openupgrade.get_legacy_name("request_hour_from")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE hr_leave SET request_hour_from = {old_request_hour_from}::float
        WHERE {old_request_hour_from} IS NOT NULL;
        """,
    )
    old_request_hour_to = openupgrade.get_legacy_name("request_hour_to")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE hr_leave SET request_hour_to = {old_request_hour_to}::float
        WHERE {old_request_hour_to} IS NOT NULL;
        """,
    )
    openupgrade.logged_query(
        env.cr,  # to avoid AttributeError: 'Float' object has no attribute 'ondelete'
        """
        DELETE FROM ir_model_fields_selection imfs
        USING ir_model_fields imf
        WHERE imfs.field_id = imf.id AND imf.model = 'hr.leave'
        AND imf.name in ('request_hour_from', 'request_hour_to')
        """,
    )


def update_states(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave
        SET state = 'confirm'
        WHERE state = 'draft'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave
        SET state = 'cancel'
        WHERE active IS DISTINCT FROM TRUE
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation
        SET state = 'cancel'
        WHERE active IS DISTINCT FROM TRUE
        """,
    )


def update_allocation_validation_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_type
        SET allocation_validation_type = 'hr'
        WHERE allocation_validation_type = 'officer'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_type
        SET allocation_validation_type = 'no_validation'
        WHERE allocation_validation_type = 'no'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.add_columns(env, _column_adds)
    refill_hr_leave_request_hours(env)
    update_states(env)
    update_allocation_validation_type(env)
    openupgrade.remove_tables_fks(
        env.cr, ["hr_employee_hr_leave_rel", "hr_employee_hr_leave_allocation_rel"]
    )
