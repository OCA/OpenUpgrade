from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "hr_skills",
        [
            "hr_resume_rule_employee",
            "hr_resume_rule_employee_hr_user",
            "hr_skill_rule_employee",
            "hr_skill_rule_employee_update",
            "hr_skill_rule_hr_user",
            "hr_skills_rule_employee_update",
        ],
        True,
    )
