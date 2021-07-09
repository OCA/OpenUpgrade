# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_field_renames = [
    ("hr.leave.type", "hr_leave_type", "validation_type", "leave_validation_type"),
]
xmlid_renames = [
    (
        "hr_holidays_calendar.hr_leave_report_calendar_rule_multi_company",
        "hr_holidays.hr_leave_report_calendar_rule_multi_company",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)

    openupgrade.rename_xmlids(env.cr, xmlid_renames)

    openupgrade.set_xml_ids_noupdate_value(
        env,
        "hr_holidays",
        [
            "hr_holidays_status_rule_multi_company",
            "hr_leave_allocation_rule_employee",
            "hr_leave_allocation_rule_employee_update",
            "hr_leave_allocation_rule_manager",
            "hr_leave_allocation_rule_officer_read",
            "hr_leave_allocation_rule_officer_update",
            "hr_leave_rule_employee",
            "hr_leave_rule_employee_unlink",
            "hr_leave_rule_employee_update",
            "hr_leave_rule_manager",
            "hr_leave_rule_multicompany",
            "hr_leave_rule_officer_update",
            "hr_leave_rule_responsible_read",
            "hr_leave_rule_responsible_update",
            "hr_leave_rule_user_read",
            "resource_leaves_base_user",
            "resource_leaves_holidays_user",
        ],
        True,
    )
