# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

renamed_xmlids = [
    ("hr_holidays.holiday_status_cl", "hr_holidays.leave_type_paid_time_off"),
    ("hr_holidays.holiday_status_sl", "hr_holidays.leave_type_sick_time_off"),
    ("hr_holidays.holiday_status_comp", "hr_holidays.leave_type_compensatory_days"),
    ("hr_holidays.holiday_status_unpaid", "hr_holidays.leave_type_unpaid"),
    (
        "hr_holidays_attendance.holiday_status_extra_hours",
        "hr_holidays.holiday_status_extra_hours",
    ),
]


def hr_leave(env):
    """
    Pre-add field hr.leave#request_date_to_period, compute from request_hour_to
    """
    openupgrade.add_fields(
        env,
        [
            (
                "request_date_to_period",
                "hr.leave",
                "hr_leave",
                "selection",
                None,
                "hr_holidays",
                "pm",
            ),
        ],
    )
    env.cr.execute(
        """
        UPDATE hr_leave
        SET
        request_date_to_period='am'
        WHERE
        request_unit_half
        AND request_hour_to <= 12
        """
    )


def hr_leave_accrual_level(env):
    """
    Map action_with_unused_accruals == 'maximum' to 'all' and set carryover_options
    to 'limited'
    Map month and day names to integers in multiple fields
    """
    openupgrade.copy_columns(
        env.cr,
        {
            "hr_leave_accrual_level": [
                ("action_with_unused_accruals", None, None),
            ]
        },
    )
    openupgrade.rename_columns(
        env.cr,
        {
            "hr_leave_accrual_level": [
                ("first_month", None),
                ("second_month", None),
                ("week_day", None),
                ("yearly_month", None),
            ]
        },
    )
    openupgrade.add_fields(
        env,
        [
            (
                "carryover_options",
                "hr.leave.accrual.level",
                "hr_leave_accrual_level",
                "selection",
                None,
                "hr_holidays",
                "unlimited",
            ),
            (
                "first_month",
                "hr.leave.accrual.level",
                "hr_leave_accrual_level",
                "selection",
                None,
                "hr_holidays",
            ),
            (
                "second_month",
                "hr.leave.accrual.level",
                "hr_leave_accrual_level",
                "selection",
                None,
                "hr_holidays",
            ),
            (
                "week_day",
                "hr.leave.accrual.level",
                "hr_leave_accrual_level",
                "selection",
                None,
                "hr_holidays",
            ),
            (
                "yearly_month",
                "hr.leave.accrual.level",
                "hr_leave_accrual_level",
                "selection",
                None,
                "hr_holidays",
            ),
        ],
    )
    env.cr.execute(
        """
        UPDATE hr_leave_accrual_level
        SET
        carryover_options='limited',
        action_with_unused_accruals='all'
        WHERE
        action_with_unused_accruals='maximum'
        """
    )
    first_month_map = [
        ("jan", "1"),
        ("feb", "2"),
        ("mar", "3"),
        ("apr", "4"),
        ("may", "5"),
        ("jun", "6"),
    ]
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("first_month"),
        "first_month",
        first_month_map,
        table="hr_leave_accrual_level",
    )
    second_month_map = [
        ("jul", "7"),
        ("aug", "8"),
        ("sep", "9"),
        ("oct", "10"),
        ("nov", "11"),
        ("dec", "12"),
    ]
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("second_month"),
        "second_month",
        second_month_map,
        table="hr_leave_accrual_level",
    )
    week_day_map = [
        ("mon", "0"),
        ("tue", "1"),
        ("wed", "2"),
        ("thu", "3"),
        ("fri", "4"),
        ("sat", "5"),
        ("sun", "6"),
    ]
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("week_day"),
        "week_day",
        week_day_map,
        table="hr_leave_accrual_level",
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("yearly_month"),
        "yearly_month",
        first_month_map + second_month_map,
        table="hr_leave_accrual_level",
    )
    openupgrade.rename_columns(
        env.cr,
        {
            "hr_leave_accrual_plan": [
                ("carryover_month", None),
            ]
        },
    )
    openupgrade.add_fields(
        env,
        [
            (
                "carryover_month",
                "hr.leave.accrual.plan",
                "hr_leave_accrual_plan",
                "selection",
                None,
                "hr_holidays",
            ),
        ],
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("carryover_month"),
        "carryover_month",
        first_month_map + second_month_map,
        table="hr_leave_accrual_plan",
    )


def hr_leave_type(env):
    """
    Convert selection yes/no fields to boolean fields;
    Rename and invert show_on_dashboard to hide_on_dashboard
    """
    openupgrade.rename_columns(
        env.cr,
        {
            "hr_leave_type": [
                ("employee_requests", None),
                ("requires_allocation", None),
                ("show_on_dashboard", "hide_on_dashboard"),
            ]
        },
    )
    openupgrade.add_fields(
        env,
        [
            (
                "employee_requests",
                "hr.leave.type",
                "hr_leave_type",
                "boolean",
                None,
                "hr_holidays",
                False,
            ),
            (
                "requires_allocation",
                "hr.leave.type",
                "hr_leave_type",
                "boolean",
                None,
                "hr_holidays",
                False,
            ),
        ],
    )
    yes_map = [("yes", True)]
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("employee_requests"),
        "employee_requests",
        yes_map,
        table="hr_leave_type",
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("requires_allocation"),
        "requires_allocation",
        yes_map,
        table="hr_leave_type",
    )
    env["ir.model.fields.selection"].search(
        [
            ("field_id.name", "in", ("employee_requests", "requires_allocation")),
            ("field_id.model_id.model", "=", "hr.leave.type"),
        ]
    ).unlink()
    env.cr.execute(
        """
        UPDATE hr_leave_type
        SET hide_on_dashboard=hide_on_dashboard IS DISTINCT FROM TRUE
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    hr_leave(env)
    hr_leave_accrual_level(env)
    hr_leave_type(env)
    openupgrade.delete_sql_constraint_safely(
        env, "hr_holidays", "hr_leave_accrual_level", "check_dates"
    )
    openupgrade.rename_xmlids(env.cr, renamed_xmlids)
