# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "note",
        [
            "note_note_create_unlink_global",
            "note_note_rule_global",
            "note_stage_rule_global",
        ],
        True,
    )
