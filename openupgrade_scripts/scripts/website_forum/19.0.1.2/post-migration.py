# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_forum", "19.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_forum",
        [
            "forum_post_template_new_answer",
            "forum_post_template_new_question",
            "forum_post_template_validation",
        ],
        ["arch_db"],
    )
