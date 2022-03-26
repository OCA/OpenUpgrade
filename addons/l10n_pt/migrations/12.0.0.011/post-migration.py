# Copyright 2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, ["l10n_pt.chart_15"])
    openupgrade.load_data(
        env.cr, "l10n_pt", "migrations/12.0.0.011/noupdate_changes.xml",
    )
