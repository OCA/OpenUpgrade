# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

from odoo.fields import Command

_deleted_xmlids = [
    "hr_attendance.hr_attendance_overtime_rule_employee_company",
    "hr_attendance.hr_attendance_rule_attendance_officer_overtime_restrict",
    "hr_attendance.hr_attendance_rule_attendance_overtime_admin",
    "hr_attendance.hr_attendance_rule_attendance_overtime_simple_user",
]


def cleanup_hr_attendance_rule_attendance_admin(env):
    """
    Remove old group from hr_attendance_rule_attendance_admin
    """
    env.ref("hr_attendance.hr_attendance_rule_attendance_admin").write(
        {
            "groups": [
                Command.unlink(env.ref("hr_attendance.group_hr_attendance_manager").id)
            ],
        }
    )


def hr_attendance_overtime_rule(env):
    """
    Load noupdate, forcecreate=False data for overtime rules, adjust with previous
    values
    """
    openupgrade.load_data(
        env,
        "hr_attendance",
        "data/hr_attendance_overtime_rule_data.xml",
        xml_transformation_filename="19.0.2.0/hr_attendance_overtime_rule_data-forcecreate.xml",
    )
    main_company = env.ref("base.main_company")
    default_rule = env.ref(
        "hr_attendance.hr_attendance_overtime_employee_schedule_rule"
    )
    default_rule.employer_tolerance = main_company.overtime_company_threshold / 60.0
    default_rule.employee_tolerance = main_company.overtime_employee_threshold / 60.0
    for company in env["res.company"].search([]):
        rule = default_rule
        if (
            main_company.overtime_company_threshold
            != company.overtime_company_threshold
            or main_company.overtime_employee_threshold
            != company.overtime_employee_threshold
        ):
            rule = default_rule.copy(
                {
                    "employer_tolerance": company.overtime_company_threshold / 60.0,
                    "employee_tolerance": company.overtime_employee_threshold / 60.0,
                    "ruleset_id": default_rule.ruleset_id.copy(
                        {
                            "company_id": company.id,
                            "rule_ids": [
                                Command.link(other_rule.copy().id)
                                for other_rule in default_rule.ruleset_id.rule_ids
                                if other_rule != default_rule
                            ],
                        }
                    ).id,
                }
            )
        env["hr.version"].search(
            [("company_id", "=", company.id)]
        ).ruleset_id = rule.ruleset_id


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_attendance", "19.0.2.0/noupdate_changes.xml")
    cleanup_hr_attendance_rule_attendance_admin(env)
    hr_attendance_overtime_rule(env)
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
