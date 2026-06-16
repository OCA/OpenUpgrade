# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "gamification", "19.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "gamification",
        ["email_template_badge_received", "mail_template_data_new_rank_reached"],
        ["body_html"],
    )
