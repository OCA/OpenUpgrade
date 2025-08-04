from openupgradelib import openupgrade, openupgrade_merge_records

from odoo import Command


def _fill_hr_candidate(env):
    # create helper
    column_adds = [
        ("hr.candidate", "old_applicant_id", "many2one"),  # helper
    ]
    openupgrade.add_columns(env, column_adds)
    # Create candidate records from applicant
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_candidate (
            partner_id, partner_name, email_from, email_cc, email_normalized,
            partner_phone, partner_phone_sanitized, phone_sanitized,
            employee_id, linkedin_profile, type_id, priority,
            availability, color, message_bounce, active,
            user_id, company_id, old_applicant_id,
            create_date, write_date, create_uid, write_uid
        )
        SELECT partner_id, partner_name, email_from, email_cc, email_normalized,
               COALESCE(partner_mobile, partner_phone),
               COALESCE(partner_mobile_sanitized, partner_phone_sanitized),
               phone_sanitized, emp_id, linkedin_profile, type_id, priority,
               availability, color, message_bounce, TRUE,
               user_id, company_id, id,
               create_date, write_date, create_uid, write_uid
        FROM hr_applicant
        WHERE candidate_id IS NULL;
        """,
    )
    # Update hr_applicant.candidate_id using helper old_applicant_id
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_applicant ha
        SET candidate_id = hc.id
        FROM hr_candidate hc
        WHERE ha.id = hc.old_applicant_id
        """,
    )
    # remove helper
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_candidate
        DROP COLUMN old_applicant_id
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
        ON CONFLICT DO NOTHING
        """,
    )
    # Fill calendar_event.candidate_id
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE calendar_event ce
        SET candidate_id = ha.candidate_id
        FROM hr_applicant ha
        WHERE ce.applicant_id = ha.id
        """,
    )
    # unify candidates
    env.cr.execute(
        """
        SELECT array_agg(id order by create_date desc), partner_id, company_id
        FROM hr_candidate
        WHERE partner_id IS NOT NULL
        GROUP BY partner_id, company_id
        HAVING COUNT(id) > 1
        """,
    )
    all_candidates = [x[0] for x in env.cr.fetchall()]
    for candidates in all_candidates:
        candidate_ids = env["hr.candidate"].browse(candidates)
        openupgrade_merge_records.merge_records(
            env,
            "hr.candidate",
            candidate_ids[1:].ids,
            candidate_ids[0].id,
            {
                "partner_id": "first_not_null",
                "partner_name": "first_not_null",
                "email_from": "first_not_null",
                "email_normalized": "first_not_null",
                "email_cc": "first_not_null",
                "partner_phone": "first_not_null",
                "partner_phone_sanitized": "first_not_null",
                "phone_sanitized": "first_not_null",
                "employee_id": "first_not_null",
                "linkedin_profile": "first_not_null",
                "type_id": "first_not_null",
                "priority": "first_not_null",
                "color": "first_not_null",
                "user_id": "first_not_null",
                "company_id": "first_not_null",
                "categ_ids": "merge",
                "availability": "max",
                "write_date": "max",
                "create_date": "min",
                "openupgrade_other_fields": "preserve",
            },
        )
    candidates = env["hr.candidate"].search([])
    for candidate in candidates:
        if len(candidate.applicant_ids) > 1:
            candidate._compute_priority()  # recompute priority
        if all(not applicant.active for applicant in candidate.applicant_ids):
            # archive inactive candidates if all applicants are inactive
            candidate.active = False
    # update attachments
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment ia
        SET res_model = 'hr.candidate', res_id = ha.candidate_id
        FROM hr_applicant ha
        WHERE ia.res_model = 'hr.applicant' AND ia.res_id = ha.id
        """,
    )


def _normalize_res_groups_implied(env):
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
    openupgrade.load_data(env, "hr_recruitment", "18.0.1.1/noupdate_changes_work.xml")
    openupgrade.delete_record_translations(
        env.cr, "hr_recruitment", ["mt_job_new"], ["description"]
    )
    openupgrade.delete_record_translations(
        env.cr,
        "hr_recruitment",
        ["refuse_reason_1", "refuse_reason_2", "refuse_reason_5", "refuse_reason_8"],
        ["name"],
    )
    _fill_hr_candidate(env)
    _normalize_res_groups_implied(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "hr_recruitment.categ_meet_interview",
            "hr_recruitment.hr_recruitment_blacklisted_emails",
        ],
    )
