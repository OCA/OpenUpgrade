# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(
        env,
        [
            (
                "is_mandatory_answer",
                "event.question",
                "event_question",
                "boolean",
                False,
                "website_event_questions",
                True,
            )
        ],
    )
