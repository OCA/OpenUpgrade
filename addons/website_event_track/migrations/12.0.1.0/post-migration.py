# Copyright 2019 Tecnativa - Jairo Llopis
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re
from psycopg2.extensions import AsIs
from openupgradelib import openupgrade


def _website_track_menu(env):
    """Transform the tracks menu to new scheme."""
    events_with_menu = env["event.event"].with_context(active_test=False) \
        .search([("menu_id", "!=", False)])
    for event in events_with_menu:
        # In v11, these fields were True if their menus existed
        website_track = website_track_proposal = False
        for menu in event.menu_id.child_id:
            menu_type = False
            if re.fullmatch(r"/event/.*/agenda", menu.url):
                menu_type = "track"
            elif re.fullmatch(r"/event/.*/track", menu.url):
                website_track = True
                menu_type = "track"
            elif re.fullmatch(r"/event/.*/track_proposal", menu.url):
                website_track_proposal = True
                menu_type = "track_proposal"
            # Create the website.event.menu reocrd if needed
            if menu_type:
                env['website.event.menu'].create({
                    'menu_id': menu.id,
                    'event_id': event.id,
                    'menu_type': menu_type,
                })
        # Update the flags according to menus presence, by SQL to avoid
        # autocreating duplicate website.menu records
        if website_track or website_track_proposal:
            env.cr.execute(
                """UPDATE %s
                   SET website_track = %s, website_track_proposal = %s
                   WHERE id = %s""",
                (AsIs(event._table),
                 website_track,
                 website_track_proposal,
                 event.id))


@openupgrade.migrate()
def migrate(env, version):
    _website_track_menu(env)
    # Noupdate data
    openupgrade.load_data(
        env.cr, 'website_event_track',
        'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'website_event_track', [
            'mail_template_data_track_confirmation',
        ],
    )
