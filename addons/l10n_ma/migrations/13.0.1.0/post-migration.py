# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "l10n_ma.tax_tag_01",
            "l10n_ma.tax_tag_02",
            "l10n_ma.tax_tag_03",
            "l10n_ma.tax_tag_04",
            "l10n_ma.tax_tag_05",
            "l10n_ma.tax_tag_06",
            "l10n_ma.tax_tag_07",
            "l10n_ma.tax_tag_08",
            "l10n_ma.tax_tag_09",
        ],
    )
