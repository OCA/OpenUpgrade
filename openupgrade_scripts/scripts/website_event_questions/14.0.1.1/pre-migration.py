from openupgradelib import openupgrade


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
    # Remove SQL view event_question_report not used anymore in Odoo v14.0
    openupgrade.logged_query(
        env.cr, "DROP VIEW IF EXISTS event_question_report CASCADE"
    )
