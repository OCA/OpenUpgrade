from openupgradelib import openupgrade


def migrate_website_event_questions_free_text(env):
    openupgrade.logged_query(
        env.cr,
        """UPDATE event_question
        SET question_type = "text_box"
        WHERE free_text = True
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """INSERT INTO event_registration_answer
            (question_id, registration_id, value_text_box)
        SELECT eaf.question_id, eaf.registration_id, eaf.answer
        FROM event_answer_free eaf
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, [("event.answer", "event.question.answer")])

    openupgrade.rename_tables(
        env.cr,
        [("event_answer", "event_question_answer")],
    )

    openupgrade.rename_fields(
        env,
        [
            (
                "event.registration.answer",
                "event_registration_answer",
                "event_answer_id",
                "value_answer_id",
            ),
            (
                "event.registration.answer",
                "event_registration_answer",
                "event_registration_id",
                "registration_id",
            ),
        ],
    )
    if openupgrade.column_exists(env.cr, "event_question", "free_text"):
        migrate_website_event_questions_free_text(env)
