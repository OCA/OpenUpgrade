from openupgradelib import openupgrade


def _fast_fill_hr_leave_employee_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave
        ADD COLUMN IF NOT EXISTS employee_company_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave hl
        SET employee_company_id = empl.company_id
        FROM hr_employee empl
        WHERE hl.employee_id IS NOT NULL AND hl.employee_id = empl.id""",
    )


def _map_hr_leave_state(env):
    openupgrade.map_values(
        env.cr,
        "state",
        "state",
        [("cancel", "refuse")],
        table="hr_leave",
    )


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
        SET approver_id = CASE
            WHEN second_approver_id IS NOT NULL THEN second_approver_id
            ELSE first_approver_id END
        WHERE state in ('refuse', 'validate')""",
    )


def _map_hr_leave_allocation_state(env):
    openupgrade.logged_query(
        env.cr,
        """UPDATE hr_leave_allocation
        SET state = 'confirm'
        WHERE state = 'validate1'""",
    )


def _convert_datetime_to_date_hr_leave_allocation_date_from(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation
        SET date_from = CASE
            WHEN date_from IS NOT NULL THEN date_from::date
            ELSE create_date::date END""",
    )


def _convert_datetime_to_date_hr_leave_allocation_date_to(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation
        SET date_to = date_to::date
        WHERE date_to IS NOT NULL""",
    )


def _fast_fill_hr_leave_allocation_employee_company_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_allocation
        ADD COLUMN IF NOT EXISTS employee_company_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave hl
        SET employee_company_id = empl.company_id
        FROM hr_employee empl
        WHERE hl.employee_id IS NOT NULL AND hl.employee_id = empl.id""",
    )


def _map_hr_leave_type_allocation_validation_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_type
        SET allocation_validation_type =
            CASE WHEN allocation_validation_type = 'hr' THEN 'set'
            ELSE 'officer' END
        WHERE allocation_validation_type IN ('hr', 'both', 'manager')
        """,
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
            CASE WHEN allocation_type = 'no' THEN 'no' ELSE 'yes' END""",
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
        WHERE hl.holiday_type = 'employee'
        """,
    )


def _fast_fill_hr_leave_multi_employee(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave
        ADD COLUMN IF NOT EXISTS multi_employee boolean""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave
        SET multi_employee =
            (SELECT COUNT(rel.hr_employee_id) > 1
            FROM hr_employee_hr_leave_rel rel
            WHERE hr_leave.id = rel.hr_leave_id
                AND hr_leave.employee_id = rel.hr_employee_id
            )""",
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
        WHERE hla.holiday_type = 'employee'
        """,
    )


def _fast_fill_hr_leave_allocation_multi_employee(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave_allocation
        ADD COLUMN IF NOT EXISTS multi_employee boolean""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_leave_allocation
        SET multi_employee =
            (SELECT COUNT(rel.hr_employee_id) > 1
            FROM hr_employee_hr_leave_allocation_rel rel
            WHERE hr_leave_allocation.id = rel.hr_leave_allocation_id
                AND hr_leave_allocation.employee_id = rel.hr_employee_id
            )""",
    )


def _create_column_hr_leave_holiday_allocation_id(env):
    # Manually create column for avoiding the automatic launch of the compute or default
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_leave
        ADD COLUMN IF NOT EXISTS holiday_allocation_id integer""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _fast_fill_hr_leave_employee_company_id(env)
    _map_hr_leave_state(env)
    _map_hr_leave_allocation_approver_id(env)
    _map_hr_leave_allocation_state(env)
    _convert_datetime_to_date_hr_leave_allocation_date_from(env)
    _convert_datetime_to_date_hr_leave_allocation_date_to(env)
    _fast_fill_hr_leave_allocation_employee_company_id(env)
    _map_hr_leave_type_allocation_validation_type(env)
    _fast_fill_hr_leave_type_employee_requests(env)
    _fast_fill_hr_leave_employee_ids(env)
    _fast_fill_hr_leave_multi_employee(env)
    _fast_fill_hr_leave_allocation_employee_ids(env)
    _fast_fill_hr_leave_allocation_multi_employee(env)
    _create_column_hr_leave_holiday_allocation_id(env)
