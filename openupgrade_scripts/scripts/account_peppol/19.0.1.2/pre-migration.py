# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

copy_columns = {
    "res_company": [
        ("account_peppol_proxy_state", None, None),
    ]
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, copy_columns)
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("account_peppol_proxy_state"),
        "account_peppol_proxy_state",
        [("in_verification", "not_registered")],
        table="res_company",
    )
