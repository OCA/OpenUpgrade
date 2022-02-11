# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_event_track_tag_name(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE event_track_tag
        SET name = 'default_name_' || id
        WHERE name IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_event_track_tag_name(env)
    openupgrade.load_data(
        env.cr, "website_event_track",
        "migrations/13.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, 'website_event_track', [
            'mail_template_data_track_confirmation',
        ],
    )
