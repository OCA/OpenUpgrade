# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def mark_recruitment_category(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE survey_survey ss
        SET category = 'hr_recruitment'
        FROM hr_job hj
        WHERE hj.survey_id = ss.id"""
    )


def remove_demo_survey_if_not_used(env):
    survey = env.ref("hr_recruitment_survey.recruitment_form")
    if (not env["hr.job"].search([("survey_id", "=", survey.id)]) and
            not survey.answer_count):
        openupgrade.delete_records_safely_by_xml_id(
            env, ["hr_recruitment_survey.recruitment_form"],
        )


@openupgrade.migrate()
def migrate(env, version):
    mark_recruitment_category(env)
    remove_demo_survey_if_not_used(env)
