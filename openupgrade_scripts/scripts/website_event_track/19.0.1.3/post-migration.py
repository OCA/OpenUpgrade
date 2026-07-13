# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "website_event_track", "19.0.1.3/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_event_track",
        ["mail_template_data_track_confirmation"],
        ["body_html"],
    )
