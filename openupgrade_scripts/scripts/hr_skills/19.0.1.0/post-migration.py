# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def hr_employee_skill_validity_dates(env):
    """
    Set hr.employee.skill#valid_from from hr.employee.skill.log
    """
    env.cr.execute(
        """
        UPDATE hr_employee_skill hes
        SET valid_from = hesl.date
        FROM
        hr_employee_skill_log hesl
        WHERE
        hes.employee_id = hesl.employee_id
        AND
        hes.skill_id = hesl.skill_id
        AND
        hes.skill_level_id = hesl.skill_level_id
        AND
        hes.skill_type_id = hesl.skill_type_id
        """
    )

    env.cr.execute(
        """
        UPDATE hr_employee_skill
        SET valid_from = create_date
        WHERE valid_from IS NULL AND create_date IS NOT NULL
        """
    )


def hr_job_job_skill_ids(env):
    """
    For every job in hr.job#skill_ids, create a default hr.job.skill entry
    (this happens only if hr_recruitment_skills has been installed in v18)
    """
    HrJobSkill = env["hr.job.skill"]
    for job in env["hr.job"].search([("skill_ids", "!=", False)]):
        hr_job_skill_vals = []
        for skill in job.skill_ids:
            vals = {
                "job_id": job.id,
                "skill_id": skill.id,
                "skill_type_id": skill.skill_type_id.id,
            }
            vals["skill_level_id"] = HrJobSkill.new(vals).skill_level_id.id
            hr_job_skill_vals.append(vals)
        env["hr.job.skill"].create(hr_job_skill_vals)


def hr_employee_certification_report_action_domain(env):
    """
    Remove domain from action
    """
    action = env.ref("hr_skills.hr_employee_certification_report_action")
    if action:
        action.domain = False


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_skills", "19.0.1.0/noupdate_changes.xml")
    hr_employee_skill_validity_dates(env)
    hr_job_job_skill_ids(env)
    hr_employee_certification_report_action_domain(env)
