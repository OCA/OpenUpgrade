from openupgradelib import openupgrade

from odoo import Command


def _set_survey_recruitment(env):
    """
    Set the survey_type to 'recruitment' for all surveys linked to HR jobs.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_survey survey
        SET survey_type = 'recruitment'
        FROM hr_job job
        WHERE job.survey_id = survey.id
        """,
    )


def _normalize_res_groups_implied(env):
    """
    Remove the implied_ids from group_hr_recruitment_interviewer
    according to the changes in Odoo 18.0.
    https://github.com/odoo/odoo/commit/027a2a66d63225abbfaef425448188007f573ac5
    """
    recruitment_interviewer = env.ref("hr_recruitment.group_hr_recruitment_interviewer")
    group_survey_user = env.ref("survey.group_survey_user")
    recruitment_interviewer.write(
        {
            "implied_ids": [(Command.unlink, group_survey_user.id)],
            "comment": "",  # Set to blank, in the hr_recruitment module it is not set.
        }
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "hr_recruitment_survey", "18.0.1.0/noupdate_changes.xml")
    _set_survey_recruitment(env)
    _normalize_res_groups_implied(env)
    openupgrade.delete_record_translations(
        env.cr,
        "hr_recruitment",
        ["group_hr_recruitment_interviewer"],
        ["comment"],
    )
