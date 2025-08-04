from openupgradelib import openupgrade

from odoo import Command


def _fill_hr_candidate(env):
    # Update hr_candidate table with hr_applicant data
    # once the table is created with all fields
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_candidate AS hc
        SET
            active = ha.active,
            create_uid = ha.create_uid,
            create_date = ha.create_date,
            write_uid = ha.write_uid,
            write_date = ha.write_date,
            company_id = ha.company_id,
            partner_id = ha.partner_id,
            partner_name = ha.partner_name,
            email_from = ha.email_from,
            email_normalized = ha.email_normalized,
            partner_phone = ha.partner_phone,
            partner_phone_sanitized = ha.partner_phone_sanitized,
            phone_sanitized = ha.phone_sanitized,
            linkedin_profile = ha.linkedin_profile,
            type_id = ha.type_id,
            availability = ha.availability,
            color = ha.color,
            priority = ha.priority,
            user_id = ha.user_id,
            employee_id = ha.emp_id
        FROM hr_applicant AS ha
        WHERE ha.candidate_id = hc.id;
        """,
    )
    # fill many2many field categ_ids
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_applicant_category_hr_candidate_rel (
            hr_candidate_id, hr_applicant_category_id
        )
        SELECT ha.candidate_id, m2m.hr_applicant_category_id
        FROM hr_applicant_hr_applicant_category_rel as m2m
            JOIN hr_applicant AS ha ON ha.id = m2m.hr_applicant_id
        WHERE ha.candidate_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """,
    )


def _normalice_res_groups_implied(env):
    """
    Remove the implied_ids from group_hr_recruitment_manager
    according to the changes in Odoo 18.0.
    https://github.com/odoo/odoo/commit/901088c76f07b6bc076fa66b76fe892be909c7a8
    https://github.com/odoo/odoo/commit/2ad420db95d47e73cff0d4c46d22b48bf83fed5f
    """
    recruitment_manager = env.ref("hr_recruitment.group_hr_recruitment_manager")
    group_hr_user = env.ref("hr.group_hr_user")
    group_mail_template = env.ref("mail.group_mail_template_editor")
    recruitment_manager.implied_ids = [
        Command.unlink(group_hr_user.id),
        Command.unlink(group_mail_template.id),
    ]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_recruitment", "18.0.1.1/noupdate_changes.xml")
    _fill_hr_candidate(env)
    _normalice_res_groups_implied(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "hr_recruitment.categ_meet_interview",
            "hr_recruitment.refuse_reason_3",
            "hr_recruitment.refuse_reason_4",
            "hr_recruitment.hr_recruitment_blacklisted_emails",
        ],
    )
