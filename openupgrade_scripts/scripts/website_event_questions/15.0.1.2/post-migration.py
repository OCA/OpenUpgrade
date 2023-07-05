# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _unlink_non_applicable_questions(env):
    """Set event_type_id = NULL on existing questions if the field `event_question` was
    not marked in the event type. This way, we preserve possible existing answers, but
    non desired questions are not done for the events of that type.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_question eq
        SET event_type_id = NULL
        FROM event_type et
        WHERE et.id = eq.event_type_id
            AND NOT et.use_questions
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "website_event_questions", "15.0.1.2/noupdate_changes.xml"
    )
    _unlink_non_applicable_questions(env)
