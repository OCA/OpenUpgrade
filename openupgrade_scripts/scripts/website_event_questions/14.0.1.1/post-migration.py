from openupgradelib import openupgrade


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
