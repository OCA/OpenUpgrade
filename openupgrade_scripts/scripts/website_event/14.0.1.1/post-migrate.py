# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

OBSOLETE_TEMPLATES = [
    "website_event.event_description_full",
    "website_event.events_list",
]


def _remove_obsolete_templates(env):
    """These customizations will fail due to non existing fields (e.g.: is_online)"""
    env["ir.ui.view"].search(
        [("key", "in", OBSOLETE_TEMPLATES), ("website_id", "!=", False)]
    ).unlink()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_event", "14.0.1.1/noupdate_changes.xml")
    _remove_obsolete_templates(env)
