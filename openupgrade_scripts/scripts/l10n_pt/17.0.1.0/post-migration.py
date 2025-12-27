# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    l10n_pt_xmlids = [
        "fiscal_position_foreign_eu",
        "fiscal_position_foreign_eu_private",
        "fiscal_position_foreign_other",
        "fiscal_position_national_customers",
    ]
    for xmlid in l10n_pt_xmlids:
        env["ir.model.data"].search(
            [("name", "=", xmlid), ("module", "=", "l10n_pt")]
        ).unlink()
