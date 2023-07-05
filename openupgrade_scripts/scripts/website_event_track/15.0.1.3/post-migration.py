# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _check_sponsors(env):
    """If any sponsor found, mark website_event_exhibitor module to be installed, as
    this is the new host for such model. Also renamed XML-IDs for commodity.
    """
    env.cr.execute("SELECT id FROM event_sponsor LIMIT 1")
    has_sponsor = env.cr.fetchone()
    env.cr.execute(
        "SELECT state FROM ir_module_module WHERE name='website_event_exhibitor'"
    )
    row = env.cr.fetchone()
    module_not_installed = row and row[0] == "uninstalled"
    if has_sponsor and module_not_installed:
        openupgrade.logged_query(
            env.cr,
            "UPDATE ir_module_module SET state='to install' "
            "WHERE name='website_event_exhibitor'",
        )
        openupgrade.rename_xmlids(
            env.cr,
            [
                (
                    "website_event_track.event_sponsor_type1",
                    "website_event_exhibitor.event_sponsor_type1",
                ),
                (
                    "website_event_track.event_sponsor_type2",
                    "website_event_exhibitor.event_sponsor_type2",
                ),
                (
                    "website_event_track.event_sponsor_type3",
                    "website_event_exhibitor.event_sponsor_type3",
                ),
                (
                    "website_event_track.event_sponsor_action_from_event",
                    "website_event_exhibitor.event_sponsor_action_from_event",
                ),
                (
                    "website_event_track.event_sponsor_type_action",
                    "website_event_exhibitor.event_sponsor_type_action",
                ),
                (
                    "website_event_track.menu_event_sponsor_type",
                    "website_event_exhibitor.menu_event_sponsor_type",
                ),
                (
                    "website_event_track.event_sponsor",
                    "website_event_exhibitor.event_sponsor",
                ),
            ],
        )
    else:
        openupgrade.delete_records_safely_by_xml_id(
            env,
            [
                "website_event_track.event_sponsor_type1",
                "website_event_track.event_sponsor_type2",
                "website_event_track.event_sponsor_type3",
            ],
        )


@openupgrade.migrate()
def migrate(env, version):
    _check_sponsors(env)
    openupgrade.load_data(
        env.cr, "website_event_track", "15.0.1.3/noupdate_changes.xml"
    )
    openupgrade.delete_record_translations(
        env.cr, "website_event_track", ["mail_template_data_track_confirmation"]
    )
