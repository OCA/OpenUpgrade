# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_applicant_activities(env):
    """Convert fields about next action to do to activities records."""
    mail_type = env.ref('mail.mail_activity_data_todo')
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO mail_activity
            (res_id, res_model_id, res_model, res_name, summary,
             activity_type_id, date_deadline, create_uid, create_date,
             write_uid, write_date,
             user_id)
         SELECT
            ha.id,  im.id, im.model, ha.name, ha.title_action,
            %s, ha.date_action, ha.create_uid, ha.create_date,
            ha.write_uid, ha.write_date,
            COALESCE(ha.user_id, hj.user_id, hd.manager_id, ha.create_uid)
         FROM hr_applicant AS ha
            INNER JOIN ir_model AS im ON im.model = 'hr.applicant'
            LEFT JOIN hr_department hd ON hd.id = ha.department_id
            LEFT JOIN hr_job hj ON hj.id = ha.job_id
         WHERE
            title_action IS NOT NULL AND
            date_action IS NOT NULL""", (mail_type.id, ),
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_applicant_activities(env)
    # Delete the action defined in previous versions
    env.ref("hr_recruitment.menu_crm_case_categ0_act_job").action_id = False
    openupgrade.load_data(
        env.cr, 'hr_recruitment', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
