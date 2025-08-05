# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _remove_survey_admin_from_default_user(env):
    """
    Default groups for default user had survey_manager in v17,
    but only survey_user in v18
    We therefore remove survey_manager from default group
    """
    default_user = env.ref("base.default_user")
    default_user.groups_id = [(3, env.ref("survey.group_survey_manager").id)]


@openupgrade.migrate()
def migrate(env, version):
    _remove_survey_admin_from_default_user(env)
    openupgrade.load_data(env, "survey", "18.0.3.7/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "base", ["module_category_marketing_surveys"], ["description"]
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "survey.survey_question_answer_rule_survey_user_cw",
            "survey.survey_question_answer_rule_survey_user_read",
            "survey.survey_question_rule_survey_user_cw",
            "survey.survey_question_rule_survey_user_read",
            "survey.survey_survey_rule_survey_user_cwu",
            "survey.survey_survey_rule_survey_user_read",
            "survey.survey_user_input_line_rule_survey_user_cw",
            "survey.survey_user_input_line_rule_survey_user_read",
            "survey.survey_user_input_rule_survey_user_cw",
            "survey.survey_user_input_rule_survey_user_read",
        ],
    )
