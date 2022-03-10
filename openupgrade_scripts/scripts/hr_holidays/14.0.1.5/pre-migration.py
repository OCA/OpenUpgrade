# Copyright (C) 2021 Open Source Integrators
# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_column_copies = {
    "hr_leave_type": [("validation_type", "allocation_validation_type", "varchar")],
    "hr_leave": [("name", "private_name", "varchar")],
    "hr_leave_allocation": [("name", "private_name", "varchar")],
}

_field_renames = [
    ("hr.leave.type", "hr_leave_type", "validation_type", "leave_validation_type"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "hr_holidays",
        [
            "hr_holidays_status_rule_multi_company",
            "hr_leave_allocation_rule_employee",
            "hr_leave_allocation_rule_employee_update",
            "hr_leave_allocation_rule_manager",
            "hr_leave_allocation_rule_multicompany",
            "hr_leave_allocation_rule_officer_read",
            "hr_leave_allocation_rule_officer_update",
            "hr_leave_report_calendar_rule_multi_company",
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
