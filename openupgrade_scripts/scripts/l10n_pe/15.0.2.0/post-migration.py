# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "l10n_pe",
        [
            "tax_group_det",
            "tax_group_exo",
            "tax_group_exp",
            "tax_group_gra",
            "tax_group_igv",
            "tax_group_ina",
            "tax_group_isc",
            "tax_group_ivap",
            "tax_group_other",
        ],
        True,
    )
