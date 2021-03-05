# Copyright 2021 bloopark systems (<https://www.bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "l10n_de_skr04",
        [
            "l10n_chart_de_skr04"
        ],
        False,
    )
