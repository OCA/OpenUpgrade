# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "gamification", "migrations/12.0.1.0/noupdate_changes.xml",
    )
    openupgrade.delete_record_translations(
        env.cr, 'gamification', [
            "email_template_badge_received",
            "email_template_goal_reminder",
            "simple_report_template",
        ],
    )
