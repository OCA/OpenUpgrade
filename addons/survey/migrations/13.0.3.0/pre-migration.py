# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_model_renames = [
    ('survey.mail.compose.message', 'survey.invite'),
]

_table_renames = [
    ('survey_mail_compose_message', 'survey_invite'),
]

_field_renames = [
    ('survey.label', 'survey_label', 'quizz_mark', 'answer_score'),
    ('survey.question', 'survey_question', 'type', 'question_type'),
    ('survey.survey', 'survey_survey', 'email_template_id', 'certification_mail_template_id'),
    ('survey.user_input', 'survey_user_input', 'type', 'input_type'),
    ('survey.user_input', 'survey_user_input', 'date_create', 'start_datetime'),
    ('survey.user_input_line', 'survey_user_input_line', 'date_create', 'value_datetime'),
    ('survey.user_input_line', 'survey_user_input_line', 'quizz_mark', 'answer_score'),
]

_field_adds = [
    ("title", "survey.question", "survey_question", "char", False, "survey"),
    ("is_page", "survey.question", "survey_question", "boolean", False, "survey"),
]

_column_renames = {
    'survey_user_input': [
        ('last_displayed_page_id', None),
    ],
    'survey_question': [
        ('page_id', None),
    ],
}

_xmlid_renames = [
    # ir.model.access
    ('survey.access_survey_label_manager', 'survey.access_survey_label_survey_manager'),
    ('survey.access_survey_label_public', 'survey.access_survey_label_all'),
    ('survey.access_survey_manager', 'survey.access_survey_survey_manager'),
    ('survey.access_survey_public', 'survey.access_survey_all'),
    ('survey.access_survey_question_manager', 'survey.access_survey_question_survey_manager'),
    ('survey.access_survey_question_public', 'survey.access_survey_question_all'),
    ('survey.access_survey_user_input_line_manager', 'survey.access_survey_user_input_line_survey_manager'),
    ('survey.access_survey_user_input_line_public', 'survey.access_survey_user_input_line_all'),
    ('survey.access_survey_user_input_manager', 'survey.access_survey_user_input_survey_manager'),
    ('survey.access_survey_user_input_public', 'survey.access_survey_user_input_all'),
    # ir.rule
    ('survey.survey_input_manager_access', 'survey.survey_user_input_rule_survey_manager'),
    ('survey.survey_input_public_access', 'survey.survey_user_input_rule_survey_user_read'),
    ('survey.survey_input_users_access', 'survey.survey_user_input_rule_survey_user_cw'),
    ('survey.survey_manager_access', 'survey.survey_survey_rule_survey_manager'),
    ('survey.survey_users_access', 'survey.survey_survey_rule_survey_user_read'),
    # mail.template
    ('survey.email_template_survey', 'survey.mail_template_user_input_invite'),
]


def move_survey_page_to_survey_question(env):
    openupgrade.add_fields(env, _field_adds)
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE survey_question
        ADD COLUMN survey_id INT4
        """,
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE survey_question sq
        SET title = sp.title, survey_id = sp.survey_id, is_page = TRUE
        FROM survey_page sp
        WHERE sp.id = sq.{}
        """.format(openupgrade.get_legacy_name('page_id'))
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    move_survey_page_to_survey_question(env)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "survey",
        [
            "survey_action_server_clean_test_answers",
        ],
        True,
    )
