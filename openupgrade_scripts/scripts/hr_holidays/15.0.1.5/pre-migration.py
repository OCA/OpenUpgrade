from openupgradelib import openupgrade

_columns_copy = {
    "hr_leave_type": [
        ("allocation_validation_type", None, None),
    ],
    "hr_leave": [
        ("state", None, None),
    ],
    "hr_leave_allocation": [
        ("state", None, None),
    ],
}


def _map_hr_leave_allocation_approver_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_allocation
        ADD COLUMN IF NOT EXISTS approver_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation
        SET approver_id = COALESCE(second_approver_id, first_approver_id)
        WHERE state in ('refuse', 'validate')""",
    )


def _convert_datetime_to_date_hr_leave_allocation_date_from(env):
    openupgrade.rename_columns(env.cr, {"hr_leave_allocation": [("date_from", None)]})
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE hr_leave_allocation ADD COLUMN date_from date""",
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE hr_leave_allocation
        SET date_from = COALESCE({
        openupgrade.get_legacy_name("date_from")}, create_date)::date""",
    )


def _convert_datetime_to_date_hr_leave_allocation_date_to(env):
    openupgrade.rename_columns(env.cr, {"hr_leave_allocation": [("date_to", None)]})
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE hr_leave_allocation ADD COLUMN date_to date""",
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE hr_leave_allocation
        SET date_to = {openupgrade.get_legacy_name("date_to")}::date
        WHERE {openupgrade.get_legacy_name("date_to")} IS NOT NULL""",
    )


def _fast_fill_hr_leave_allocation_accrual_plan_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_allocation
        ADD COLUMN IF NOT EXISTS accrual_plan_id integer""",
    )


def refill_hr_leave_type_allocation_validation_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_type
        SET allocation_validation_type = CASE
            WHEN allocation_type = 'fixed_allocation' THEN 'officer'
            WHEN allocation_type = 'fixed' THEN 'set'
            ELSE 'no' END
        WHERE allocation_validation_type IS NOT NULL""",
    )


def _fast_fill_hr_leave_type_employee_requests(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_type
        ADD COLUMN IF NOT EXISTS employee_requests varchar""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_type
        SET employee_requests =
            CASE WHEN allocation_type = 'fixed_allocation' THEN 'yes' ELSE 'no' END""",
    )


def _fast_fill_hr_leave_employee_ids(env):
    # Manually create tables for avoiding the automatic launch of the compute or default
    # FK constraints and indexes will be added by ORM
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TABLE IF NOT EXISTS hr_employee_hr_leave_rel
        (hr_leave_id integer, hr_employee_id integer)
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_employee_hr_leave_rel (hr_leave_id, hr_employee_id)
        SELECT hl.id, hl.employee_id
        FROM hr_leave hl
        WHERE hl.holiday_type = 'employee' AND hl.employee_id IS NOT NULL
        """,
    )


def _fast_fill_hr_leave_multi_employee(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave
        ADD COLUMN IF NOT EXISTS multi_employee bool""",
    )


def _fast_fill_hr_leave_allocation_employee_ids(env):
    # Manually create tables for avoiding the automatic launch of the compute or default
    # FK constraints and indexes will be added by ORM
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TABLE IF NOT EXISTS hr_employee_hr_leave_allocation_rel
        (hr_leave_allocation_id integer, hr_employee_id integer)""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_employee_hr_leave_allocation_rel (
            hr_leave_allocation_id, hr_employee_id)
        SELECT hla.id, hla.employee_id
        FROM hr_leave_allocation hla
        WHERE hla.holiday_type = 'employee' AND hla.employee_id IS NOT NULL
        """,
    )


def _fast_fill_hr_leave_allocation_multi_employee(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_allocation
        ADD COLUMN IF NOT EXISTS multi_employee boolean""",
    )


def fill_hr_leave_allocation_lastcall(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_allocation
        ADD COLUMN IF NOT EXISTS lastcall date""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation
        SET lastcall = write_date::date""",
    )


def delete_sql_constraints(env):
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave_allocation", "duration_check"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave_allocation", "type_value"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave", "type_value"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave_allocation", "interval_number_check"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave_allocation", "number_per_interval_check"
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
    _map_hr_leave_allocation_approver_id(env)
    _convert_datetime_to_date_hr_leave_allocation_date_from(env)
    _convert_datetime_to_date_hr_leave_allocation_date_to(env)
    _fast_fill_hr_leave_allocation_accrual_plan_id(env)
    refill_hr_leave_type_allocation_validation_type(env)
    _fast_fill_hr_leave_type_employee_requests(env)
    _fast_fill_hr_leave_employee_ids(env)
    _fast_fill_hr_leave_multi_employee(env)
    _fast_fill_hr_leave_allocation_employee_ids(env)
    _fast_fill_hr_leave_allocation_multi_employee(env)
    fill_hr_leave_allocation_lastcall(env)
    delete_sql_constraints(env)
