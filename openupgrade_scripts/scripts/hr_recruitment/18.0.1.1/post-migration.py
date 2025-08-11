from openupgradelib import openupgrade

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
        WHERE candidate_id IS NULL AND partner_id IS NULL;
        """,
    )
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
        SELECT
            partner_id,
            partner_name,
            email_from, email_cc, email_normalized,
            partner_phone, partner_phone_sanitized,
            phone_sanitized, emp_id, linkedin_profile,
            type_id, priority,
            availability, color, message_bounce, TRUE as active,
            user_id, company_id, id as old_applicant_id,
            create_date, write_date, create_uid, write_uid
        FROM (
            SELECT
                partner_id,
                FIRST_VALUE(CASE WHEN partner_name IS NOT NULL THEN partner_name END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS partner_name,
                FIRST_VALUE(CASE WHEN email_from IS NOT NULL THEN email_from END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS email_from,
                FIRST_VALUE(CASE WHEN email_cc IS NOT NULL THEN email_cc END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS email_cc,
                FIRST_VALUE(
                    CASE WHEN email_normalized IS NOT NULL THEN email_normalized END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS email_normalized,
                FIRST_VALUE(
                    CASE WHEN COALESCE(partner_mobile, partner_phone) IS NOT NULL
                    THEN COALESCE(partner_mobile, partner_phone) END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS partner_phone,
                FIRST_VALUE(CASE WHEN COALESCE(
                        partner_mobile_sanitized, partner_phone_sanitized) IS NOT NULL
                        THEN COALESCE(partner_mobile_sanitized, partner_phone_sanitized
                        ) END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS partner_phone_sanitized,
                FIRST_VALUE(
                    CASE WHEN phone_sanitized IS NOT NULL THEN phone_sanitized END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS phone_sanitized,
                FIRST_VALUE(CASE WHEN emp_id IS NOT NULL THEN emp_id END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS emp_id,
                FIRST_VALUE(
                    CASE WHEN linkedin_profile IS NOT NULL THEN linkedin_profile END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS linkedin_profile,
                FIRST_VALUE(CASE WHEN type_id IS NOT NULL THEN type_id END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS type_id,
                FIRST_VALUE(CASE WHEN priority IS NOT NULL THEN priority END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS priority,
                MAX(CASE WHEN availability IS NOT NULL THEN availability END)
                    OVER (PARTITION BY partner_id, company_id) AS availability,
                FIRST_VALUE(CASE WHEN color IS NOT NULL THEN color END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS color,
                FIRST_VALUE(
                        CASE WHEN message_bounce IS NOT NULL THEN message_bounce END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS message_bounce,
                FIRST_VALUE(CASE WHEN user_id IS NOT NULL THEN user_id END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS user_id,
                company_id,
                id,
                MIN(CASE WHEN create_date IS NOT NULL THEN create_date END)
                    OVER (PARTITION BY partner_id, company_id) AS create_date,
                MAX(CASE WHEN write_date IS NOT NULL THEN write_date END)
                    OVER (PARTITION BY partner_id, company_id) AS write_date,
                FIRST_VALUE(CASE WHEN create_uid IS NOT NULL THEN create_uid END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS create_uid,
                FIRST_VALUE(CASE WHEN write_uid IS NOT NULL THEN write_uid END)
                    OVER (PARTITION BY partner_id, company_id ORDER BY create_date DESC
                    ) AS write_uid,
                ROW_NUMBER() OVER (
                    PARTITION BY partner_id, company_id ORDER BY create_date DESC) AS rn
            FROM hr_applicant
            WHERE candidate_id IS NULL AND partner_id IS NOT NULL
        ) ranked
        WHERE rn = 1;
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
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_applicant ha
        SET candidate_id = hc.id
        FROM hr_candidate hc
        WHERE ha.candidate_id IS NULL AND ha.partner_id = hc.partner_id
            AND (ha.company_id = hc.company_id
                OR (ha.company_id IS NULL AND hc.company_id IS NULL))
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
    # duplicate attachments
    env.cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'ir_attachment'
        """
    )
    attachment_columns = [
        x[0] for x in env.cr.fetchall() if x[0] not in ["id", "res_model", "res_id"]
    ]
    select_columns = ",".join(["ia." + x for x in attachment_columns])
    insert_columns = ",".join(attachment_columns)
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO ir_attachment (res_model,res_id,{insert_columns})
        SELECT 'hr.candidate',ha.candidate_id,{select_columns}
        FROM ir_attachment ia
        JOIN hr_applicant ha ON ia.res_model = 'hr.applicant' AND ia.res_id = ha.id
        """,
    )
    candidates = env["hr.candidate"].search([])
    for candidate in candidates:
        if len(candidate.applicant_ids) > 1:
            candidate._compute_priority()  # recompute priority
        if all(not applicant.active for applicant in candidate.applicant_ids):
            # archive inactive candidates if all applicants are inactive
            candidate.active = False


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
