# Copyright 2026 Le Filament
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _assign_default_leave_type(env):
    """
    We try to compute most probable leave type for FR companies
    in the following order :
        1. default leave type from hr_holidays still active
        2. leave type with most common default configuration
        3. leave type accessible to that company, configured in days
        or half days and of type = "leave"
        for case 2 or 3, ordering by sequence and taking the first found
    """
    fr_company_ids = (
        env["res.company"].search([]).filtered(lambda c: c.country_id.code == "FR")
    )
    default_leave_type = env.ref("hr_holidays.holiday_status_cl", False)
    for company in fr_company_ids:
        if (
            default_leave_type
            and default_leave_type.active
            and default_leave_type.company_id.id in [False, company.id]
        ):
            leave_type = default_leave_type
        else:
            leave_type = env["hr.leave.type"].search(
                [
                    ("company_id", "in", [False, company.id]),
                    ("requires_allocation", "=", "yes"),
                    ("employee_requests", "=", "no"),
                    ("request_unit", "in", ["day", "half_day"]),
                    ("leave_validation_type", "!=", "no_validation"),
                    ("time_type", "=", "leave"),
                ],
                order="sequence asc",
                limit=1,
            )
            if not leave_type:
                leave_type = env["hr.leave.type"].search(
                    [
                        ("company_id", "in", [False, company.id]),
                        ("request_unit", "in", ["day", "half_day"]),
                        ("time_type", "=", "leave"),
                    ],
                    order="sequence asc",
                    limit=1,
                )
        company.l10n_fr_reference_leave_type = leave_type


@openupgrade.migrate(no_version=True)
def migrate(env, version):
    _assign_default_leave_type(env)
