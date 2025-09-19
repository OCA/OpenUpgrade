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


def split_employee_leaves(env):
    for table in ["hr_leave", "hr_leave_allocation"]:
        env.cr.execute(
            f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
            """
        )
        columns = ", ".join(
            [x[0] for x in env.cr.fetchall() if x[0] not in ("id", "employee_id")]
        )
        leave_employees = []
        # case multi_employee
        env.cr.execute(
            f"""
            SELECT leave.id, 'employee', array_agg(rel.hr_employee_id) as employee_ids
            FROM {table} AS leave
            JOIN hr_employee_{table}_rel rel ON rel.{table}_id = leave.id
            WHERE leave.holiday_type = 'employee' AND leave.multi_employee
            GROUP BY leave.id
            """
        )
        leave_employees.extend(env.cr.fetchall())
        # case company
        env.cr.execute(
            f"""
            SELECT leave.id, 'company', array_agg(he.id) as employee_ids
            FROM {table} AS leave
            JOIN hr_employee he ON he.company_id = leave.mode_company_id
            WHERE leave.holiday_type = 'company'
            GROUP BY leave.id
            """
        )
        leave_employees.extend(env.cr.fetchall())
        # case category
        env.cr.execute(
            f"""
            SELECT leave.id, 'category', array_agg(rel.employee_id) as employee_ids
            FROM {table} AS leave
            JOIN employee_category_rel rel ON rel.category_id = leave.category_id
            WHERE leave.holiday_type = 'category'
            GROUP BY leave.id
            """
        )
        leave_employees.extend(env.cr.fetchall())
        # case department
        env.cr.execute(
            f"""
            SELECT leave.id, 'department', array_agg(he.id) as employee_ids
            FROM {table} AS leave
            JOIN hr_employee he ON he.department_id = leave.department_id
            WHERE leave.holiday_type = 'department'
            GROUP BY leave.id
            """
        )
        leave_employees.extend(env.cr.fetchall())
        for table_id, holiday_type, employee_ids in leave_employees:
            employees = env["hr.employee"].browse(employee_ids)
            if employee_ids:
                openupgrade.logged_query(
                    env.cr,
                    f"""
                    UPDATE {table}
                    SET employee_id = {employees[0].id}
                    WHERE id = {table_id}
                    """,
                )
                if holiday_type != "employee":
                    openupgrade.logged_query(
                        env.cr,
                        f"""
                        UPDATE {table}
                        SET holiday_type = 'employee'
                        WHERE id = {table_id}
                        """,
                    )
                for employee in employees[1:]:
                    openupgrade.logged_query(
                        env.cr,
                        f"""
                        INSERT INTO {table} (employee_id, {columns})
                        SELECT {employee.id}, {columns}
                        FROM {table}
                        WHERE id = {table_id}
                        """,
                    )
            else:
                openupgrade.logged_query(
                    env.cr,
                    f"""
                    DELETE FROM {table} WHERE id = {table_id}
                    """,
                )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "hr_leave_allocation", "name"):  # from 13.0
        openupgrade.rename_columns(env.cr, {"hr_leave_allocation": [("name", False)]})
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.add_columns(env, _column_adds)
    refill_hr_leave_request_hours(env)
    update_states(env)
    update_allocation_validation_type(env)
    openupgrade.remove_tables_fks(
        env.cr, ["hr_employee_hr_leave_rel", "hr_employee_hr_leave_allocation_rel"]
    )
    split_employee_leaves(env)
