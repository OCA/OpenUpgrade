# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    "survey_user_input": [
        ("state", None, None),
    ],
    "survey_user_input_line": [
        ("answer_type", None, None),
    ],
    "survey_question": [
        ("question_type", None, None),
    ],
}

_field_renames = [
    ("survey.label", "survey_label", "question_id_2", "matrix_question_id"),
    ("survey.question", "survey_question", "labels_ids", "suggested_answer_ids"),
    ("survey.question", "survey_question", "labels_ids_2", "matrix_row_ids"),
    (
        "survey.user_input_line",
        "survey_user_input_line",
        "value_suggested",
        "suggested_answer_id",
    ),
    (
        "survey.user_input_line",
        "survey_user_input_line",
        "value_suggested_row",
        "matrix_row_id",
    ),
    (
        "survey.user_input_line",
        "survey_user_input_line",
        "value_text",
        "value_char_box",
    ),
    (
        "survey.user_input_line",
        "survey_user_input_line",
        "value_number",
        "value_numerical_box",
    ),
    (
        "survey.user_input_line",
        "survey_user_input_line",
        "value_free_text",
        "value_text_box",
    ),
    ("survey.survey", "survey_survey", "certificate", "certification"),
    ("survey.survey", "survey_survey", "thank_you_message", "description_done"),
    ("survey.survey", "survey_survey", "passing_score", "scoring_success_min"),
    ("survey.user_input", "survey_user_input", "token", "access_token"),
    ("survey.user_input", "survey_user_input", "quizz_score", "scoring_percentage"),
    ("survey.user_input", "survey_user_input", "quizz_passed", "scoring_success"),
    (
        "survey.user_input",
        "survey_user_input",
        "question_ids",
        "predefined_question_ids",
    ),
]
_model_renames = [
    ("survey.user_input_line", "survey.user_input.line"),
    ("survey.label", "survey.question.answer"),
]
_table_renames = [("survey_label", "survey_question_answer")]
_xmlid_renames = [
    ("survey.access_survey_label_all", "survey.access_survey_question_answer_all"),
    (
        "survey.access_survey_label_survey_manager",
        "survey.access_survey_question_answer_survey_manager",
    ),
    (
        "survey.access_survey_label_survey_user",
        "survey.access_survey_question_answer_survey_user",
    ),
    ("survey.access_survey_label_user", "survey.access_survey_question_answer_user"),
    (
        "survey.survey_label_rule_survey_manager",
        "survey.survey_question_answer_rule_survey_manager",
    ),
    (
        "survey.survey_label_rule_survey_user_cw",
        "survey.survey_question_answer_rule_survey_user_cw",
    ),
    (
        "survey.survey_label_rule_survey_user_read",
        "survey.survey_question_answer_rule_survey_user_read",
    ),
    ("survey.action_survey_user_input_line", "survey.survey_user_input_line_action"),
    ("survey.action_survey_label_form", "survey.survey_question_answer_action"),
    ("survey.survey_label_search", "survey.survey_question_answer_view_search"),
    ("survey.survey_label_tree", "survey.survey_question_answer_view_tree"),
    ("survey.survey_user_input_line_form", "survey.survey_user_input_line_view_form"),
    ("survey.survey_response_line_search", "survey.survey_user_input_line_view_search"),
    ("survey.survey_response_line_tree", "survey.survey_response_line_view_tree"),
    ("survey.403", "survey.survey_403_page"),
    ("survey.auth_required", "survey.survey_auth_required"),
    ("survey.date", "survey.question_date"),
    ("survey.datetime", "survey.question_datetime"),
    ("survey.matrix", "survey.question_matrix"),
    ("survey.multiple_choice", "survey.question_multiple_choice"),
    ("survey.numerical_box", "survey.question_numerical_box"),
    ("survey.result_choice", "survey.question_result_choice"),
    ("survey.result_comments", "survey.question_result_comments"),
    ("survey.result_matrix", "survey.question_result_matrix"),
    ("survey.result_number", "survey.question_result_number_or_date"),
    ("survey.result_text", "survey.question_result_text"),
    ("survey.textbox", "survey.question_char_box"),
    ("survey.free_text", "survey.question_text_box"),
    ("survey.pagination", "survey.question_table_pagination"),
    ("survey.retake_survey_button", "survey.survey_button_retake"),
    ("survey.simple_choice", "survey.question_simple_choice"),
    ("survey.survey_expired", "survey.survey_closed_expired"),
    ("survey.survey_void", "survey.survey_void_content"),
    ("survey.survey_print", "survey.survey_page_print"),
    ("survey.question", "survey.question_container"),
    ("survey.back", "survey.survey_button_form_view"),
    ("survey.survey", "survey.survey_page_fill"),
    ("survey.page", "survey.survey_fill_form"),
    ("survey.survey_header", "survey.survey_fill_header"),
    ("survey.survey_init", "survey.survey_fill_form_start"),
    ("survey.sfinished", "survey.survey_fill_form_done"),
    ("survey.result", "survey.survey_page_statistics"),
]


def fill_survey_survey_session_state(env):
    # done in pre-migration because this field is used in some computes
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("skip", "in_progress")],
        table="survey_user_input",
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE survey_survey
        ADD COLUMN session_state varchar""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE survey_survey
        ADD COLUMN session_start_time timestamp without time zone""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_survey ss
        SET session_state = CASE WHEN sui.state = 'new' THEN 'ready'
            WHEN sui.state = 'in_progress' THEN 'in_progress'
            ELSE NULL END, session_start_time = CASE
            WHEN sui.state IN ('new', 'in_progress') THEN ss.write_date
            ELSE NULL END
        FROM survey_user_input sui
        WHERE sui.survey_id = ss.id AND ss.state != 'draft'""",
    )


def fast_fill_survey_input_some_values(env):
    # some new computes depend of this is_session_answer field
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE survey_user_input
        ADD COLUMN is_session_answer boolean""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE survey_user_input
        ADD COLUMN nickname varchar""",
    )
    # is_session_answer
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_user_input sui
        SET is_session_answer = TRUE, start_datetime = sui.write_date
        FROM survey_survey ss
        WHERE sui.survey_id = ss.id AND ss.session_state IN ('ready', 'in_progress')""",
    )
    # nickname
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_user_input sui
        SET nickname = rp.name
        FROM res_partner rp
        WHERE sui.partner_id = rp.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_user_input sui
        SET nickname = sui.email
        WHERE sui.nickname IS NULL""",
    )


def fill_survey_user_input_line_answer_is_correct(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE survey_user_input_line
        ADD COLUMN answer_is_correct boolean""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_user_input_line suil
        SET answer_is_correct = sqa.is_correct
        FROM survey_question_answer sqa, survey_question sq
        WHERE suil.suggested_answer_id = sqa.id AND suil.question_id = sq.id
            AND sq.question_type IN ('simple_choice', 'multiple_choice')""",
    )


def fill_survey_session_code(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE survey_survey ADD COLUMN session_code varchar;"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE survey_survey ss
        SET session_code = sub.number || ''
        FROM (
            SELECT id, ROW_NUMBER() OVER(ORDER BY id) + 999 AS number
            FROM survey_survey
        ) sub
        WHERE sub.id = ss.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fill_survey_survey_session_state(env)
    fast_fill_survey_input_some_values(env)
    fill_survey_user_input_line_answer_is_correct(env)
    fill_survey_session_code(env)
    # Disappeared constraint
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE survey_survey
           DROP CONSTRAINT IF EXISTS survey_survey_certificate_check""",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["survey.constraint_survey_survey_certificate_check"]
    )
