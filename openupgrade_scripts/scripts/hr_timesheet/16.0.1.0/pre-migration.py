from openupgradelib import openupgrade


def update_rename_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_employee
        ADD COLUMN IF NOT EXISTS hourly_cost numeric
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee
        SET hourly_cost = timesheet_cost
        """,
    )


def create_ancestor_task_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS ancestor_task_id integer
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line AS aal
        SET ancestor_task_id = pt.ancestor_id
        FROM project_task AS pt
        WHERE pt.id = aal.task_id
        """,
    )


def create_manager_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_analytic_line
        ADD COLUMN IF NOT EXISTS manager_id integer
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line AS aal
        SET manager_id = he.parent_id
        FROM hr_employee AS he
        WHERE he.id = aal.employee_id
        """,
    )


def delete_constraint_project_task_create_timesheet_time_positive(env):
    openupgrade.delete_sql_constraint_safely(
        env,
        "hr_timesheet",
        "project_task",
        "create_timesheet_time_positive",
    )


@openupgrade.migrate()
def migrate(env, version):
    update_rename_field(env)
    create_ancestor_task_id(env)
    create_manager_id(env)
    delete_constraint_project_task_create_timesheet_time_positive(env)
