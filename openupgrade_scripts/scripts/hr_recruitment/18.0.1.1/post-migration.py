from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Create candidate records from applicant
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO hr_candidate (
            partner_name, email_from, email_cc, partner_phone,
            linkedin_profile, type_id, priority,
            availability, create_date, write_date
        )
        SELECT partner_name, email_from, email_cc, partner_phone,
               linkedin_profile, type_id, priority,
               availability, NOW(), NOW()
        FROM hr_applicant
        WHERE candidate_id IS NULL;
        """,
    )

    # Update hr_applicant.candidate_id using matching logic
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_applicant AS a
        SET candidate_id = match.candidate_id
        FROM (
            SELECT a.id AS applicant_id, c.id AS candidate_id
            FROM hr_applicant a
            JOIN hr_candidate c
              ON c.partner_name = a.partner_name
             AND COALESCE(c.email_from, '') = COALESCE(a.email_from, '')
             AND COALESCE(c.partner_phone, '') = COALESCE(a.partner_phone, '')
             AND COALESCE(c.email_cc, '') = COALESCE(a.email_cc, '')
             AND COALESCE(c.linkedin_profile, '') = COALESCE(a.linkedin_profile, '')
             AND c.type_id IS NOT DISTINCT FROM a.type_id
             AND c.priority IS NOT DISTINCT FROM a.priority
             AND c.availability IS NOT DISTINCT FROM a.availability
        ) AS match
        WHERE a.id = match.applicant_id;
        """,
    )
