# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_deleted_xmlids = [
    "hr_recruitment.hr_candidate_comp_rule",
    "hr_recruitment.hr_candidate_interviewer_rule",
    "hr_recruitment.hr_candidate_user_rule",
]


def hr_candidate2hr_applicant(env):
    """
    hr.candidate and hr.applicant have been merged. Copy data for nonstored related
    v18 fields from hr_candidate to hr_applicant where they are stored in v19.
    """
    field_names = [
        "availability",
        "color",
        "email_from",
        "email_normalized",
        "employee_id",
        "linkedin_profile",
        "partner_id",
        "partner_name",
        "partner_phone",
        "partner_phone_sanitized",
        "type_id",
        "message_bounce",
    ]
    updates = ", ".join(
        f"{field_name} = hr_candidate.{field_name}" for field_name in field_names
    )
    updates += ", phone_sanitized=hr_candidate.partner_phone_sanitized"

    env.cr.execute(
        f"""
        UPDATE hr_applicant
        SET
        {updates}
        FROM {openupgrade.get_legacy_name("hr_candidate")} hr_candidate
        WHERE
        hr_applicant.candidate_id=hr_candidate.id
        """
    )


def hr_candidate_properties2hr_applicant_properties(env):
    """
    Merge applicant and candidate properties
    Merge property definitions from companies into jobs' applicant property definitions
    if there are v18 candidates setting them.
    Ignore applicants not linked to a job
    """
    env.cr.execute(
        f"""
        UPDATE hr_applicant
        SET applicant_properties=
            COALESCE(applicant_properties, '{{}}') ||
            hr_candidate.candidate_properties
        FROM {openupgrade.get_legacy_name("hr_candidate")} hr_candidate
        WHERE
        hr_applicant.candidate_id=hr_candidate.id
        AND
        hr_candidate.candidate_properties IS NOT NULL
        """
    )
    if env.cr.rowcount:
        env.cr.execute(
            f"""
            UPDATE hr_job
            SET applicant_properties_definition=
                COALESCE(applicant_properties_definition, '[]') ||
                res_company.candidate_properties_definition
            FROM res_company
            WHERE
            (
                hr_job.company_id=res_company.id
                OR
                hr_job.company_id IS NULL
            )
            AND
            res_company.candidate_properties_definition IS NOT NULL
            AND
            exists (
                SELECT
                hr_applicant.id
                FROM hr_applicant
                JOIN
                {openupgrade.get_legacy_name("hr_candidate")} hr_candidate
                ON hr_applicant.candidate_id=hr_candidate.id
                WHERE
                hr_candidate.candidate_properties IS NOT NULL
                AND
                hr_applicant.job_id=hr_job.id
                AND
                hr_candidate.company_id=res_company.id
            )
            """
        )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_recruitment", "19.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "hr_recruitment",
        [
            "email_template_data_applicant_congratulations",
            "email_template_data_applicant_interest",
            "email_template_data_applicant_not_interested",
            "email_template_data_applicant_refuse",
        ],
        ["body_html"],
    )
    openupgrade.delete_records_safely_by_xml_id(env, _deleted_xmlids)
    hr_candidate2hr_applicant(env)
    hr_candidate_properties2hr_applicant_properties(env)
