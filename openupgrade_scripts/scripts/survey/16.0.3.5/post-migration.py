# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _empty_images_on_answers(env):
    """Clean images on those answers that had the check unmarked on the question, as
    they didn't show the image in v15 even if they have one loaded. Now, not having the
    check, the image will be displayed always.
    """
    env.cr.execute("SELECT id FROM survey_question WHERE NOT allow_value_image")
    question_ids = env.cr.fetchall()
    answers = env["survey.question.answer"].search(
        [("value_image", "!=", False), ("question_id", "in", question_ids)]
    )
    answers.value_image = False


@openupgrade.migrate()
def migrate(env, version):
    _empty_images_on_answers(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, ["survey.survey_action_server_clean_test_answers"]
    )
