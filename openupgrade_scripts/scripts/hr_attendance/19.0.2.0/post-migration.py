# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_deleted_xmlids = [
    "hr_attendance.hr_attendance_overtime_rule_employee_company",
    "hr_attendance.hr_attendance_rule_attendance_officer_overtime_restrict",
    "hr_attendance.hr_attendance_rule_attendance_overtime_admin",
    "hr_attendance.hr_attendance_rule_attendance_overtime_simple_user",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_attendance", "19.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
