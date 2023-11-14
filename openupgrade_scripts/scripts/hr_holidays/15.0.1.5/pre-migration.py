# Copyright 2023 Viindoo - tranngocson1996
# Copyright 2023 ForgeFlow - Miquel Raich
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
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


def _assign_allocation_dates(env):
    """On v14, date_from and date_to fields on hr.leave.allocation were used for
    assignation accruals.

    Now, these fields are used for the allocation validity interval, transferred from
    the leave type.
    """
    openupgrade.rename_columns(
        env.cr, {"hr_leave_allocation": [("date_from", None), ("date_to", None)]}
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE hr_leave_allocation ADD COLUMN date_from date"
    )
    # date_from is required, so we should provide a fallback value
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation hla
        SET date_from = COALESCE(hlt.validity_start, hlt.create_date::date)
        FROM hr_leave_type hlt
        WHERE hlt.id = hla.holiday_status_id
        """,
    )
    openupgrade.logged_query(
        env.cr, "ALTER TABLE hr_leave_allocation ADD COLUMN date_to date"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation hla
        SET date_to = hlt.validity_stop
        FROM hr_leave_type hlt
        WHERE hlt.id = hla.holiday_status_id
        """,
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
    _assign_allocation_dates(env)
    _fast_fill_hr_leave_allocation_accrual_plan_id(env)
    refill_hr_leave_type_allocation_validation_type(env)
    _fast_fill_hr_leave_type_employee_requests(env)
    _fast_fill_hr_leave_employee_ids(env)
    _fast_fill_hr_leave_multi_employee(env)
    _fast_fill_hr_leave_allocation_employee_ids(env)
    _fast_fill_hr_leave_allocation_multi_employee(env)
    fill_hr_leave_allocation_lastcall(env)
    delete_sql_constraints(env)
