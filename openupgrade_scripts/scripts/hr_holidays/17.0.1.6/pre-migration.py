# Copyright 2024- Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_model_renames = [
    ("hr.leave.stress.day", "hr.leave.mandatory.day"),
]

_table_renames = [
    ("hr_leave_stress_day", "hr_leave_mandatory_day"),
    (
        "hr_department_hr_leave_stress_day_rel",
        "hr_department_hr_leave_mandatory_day_rel",
    ),
]

_column_renames = {
    "hr_department_hr_leave_mandatory_day_rel": [
        ("hr_leave_stress_day_id", "hr_leave_mandatory_day_id")
    ],
}

_field_add = [
    (
        "number_of_hours",
        "hr.leave",
        "hr_leave",
        "float",
        None,
        "hr_holidays",
        0.0,
    ),
]


def _pre_create_accrual_plan_active(cr):
    """
    Precreate column with default value true, then remove default from SQL
    """
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE hr_leave_accrual_plan ADD COLUMN active boolean DEFAULT true
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE hr_leave_accrual_plan ALTER COLUMN active DROP DEFAULT
        """,
    )


def _hr_leave_company_id(cr):
    """Create and set company_id value in the same order than new compute
    (employee_company_id, mode_company_id, department_id.company_id)
    """
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE hr_leave
        ADD COLUMN IF NOT EXISTS company_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        cr,
        """UPDATE hr_leave AS leave
        SET company_id = CASE
            WHEN employee_company_id IS NOT NULL THEN employee_company_id
            WHEN mode_company_id IS NOT NULL THEN mode_company_id
            ELSE NULL
            END
        WHERE leave.company_id IS NULL""",
    )
    openupgrade.logged_query(
        cr,
        """UPDATE hr_leave AS leave
        SET company_id = d.company_id
        FROM hr_department AS d
        WHERE leave.company_id IS NULL AND leave.department_id = d.id""",
    )


def _map_leave_accrual_level_action(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_level
        SET action_with_unused_accruals = CASE
                WHEN maximum_leave > 0 AND postpone_max_days > 0  THEN 'maximum'
                ELSE 'all'
                END
        WHERE action_with_unused_accruals = 'postponed';
        """,
    )


def _map_leave_accrual_level_added_value_type(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_level
        SET added_value_type = 'day'
        WHERE added_value_type = 'days';
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_level
        SET added_value_type = 'hour'
        WHERE added_value_type = 'hours';
        """,
    )


def _map_leave_allocation_state(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_allocation
        SET state = 'confirm'
        WHERE state = 'draft';
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_allocation
        SET state = 'refuse'
        WHERE state = 'cancel';
        """,
    )


def _set_is_based_on_worked_time(cr):
    openupgrade.logged_query(
        cr,
        """
        ALTER TABLE hr_leave_accrual_plan
            ADD COLUMN IF NOT EXISTS is_based_on_worked_time BOOLEAN;
        """,
    )
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_leave_accrual_plan plan
        SET is_based_on_worked_time = subquery.max_value::BOOLEAN
        FROM (
            SELECT accrual_plan_id, MAX(is_based_on_worked_time::INT) AS max_value
            FROM hr_leave_accrual_level
            GROUP BY accrual_plan_id
        ) subquery
        WHERE subquery.accrual_plan_id = plan.id;
        """,
    )


def _delete_sql_constraints(env):
    # Delete constraints to recreate it
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave_accrual_level", "check_dates"
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.add_fields(env, _field_add)
    _pre_create_accrual_plan_active(env.cr)
    _hr_leave_company_id(env.cr)
    _map_leave_accrual_level_action(env.cr)
    _map_leave_accrual_level_added_value_type(env.cr)
    _map_leave_allocation_state(env.cr)
    _set_is_based_on_worked_time(env.cr)
    _delete_sql_constraints(env)
