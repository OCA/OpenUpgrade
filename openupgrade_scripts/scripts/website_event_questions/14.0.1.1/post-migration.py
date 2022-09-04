from openupgradelib import openupgrade


def migrate_website_event_questions_free_text(env):
    openupgrade.logged_query(
        env.cr,
        """UPDATE event_question
        SET question_type = 'text_box'
        WHERE free_text
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
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_registration_answer era
        SET question_id = eqa.question_id
        FROM event_question_answer eqa
        WHERE era.value_answer_id = eqa.id
        """,
    )
    if openupgrade.column_exists(env.cr, "event_question", "free_text"):
        migrate_website_event_questions_free_text(env)
