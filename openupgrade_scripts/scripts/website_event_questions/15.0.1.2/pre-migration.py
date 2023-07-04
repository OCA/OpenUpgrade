# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "website_event_questions.event_question_all",
        "website_event_questions.access_event_question",
    ),
    (
        "website_event_questions.event_question_event_user",
        "website_event_questions.access_event_question_user",
    ),
    (
        "website_event_questions.event_question_answer_all",
        "website_event_questions.access_event_question_answer",
    ),
    (
        "website_event_questions.event_question_answer_event_user",
        "website_event_questions.access_event_question_answer_user",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
