# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_reason_code_map = [
    ("VATEX_EU_AE", "VATEX-EU-AE"),
    ("VATEX_EU_D", "VATEX-EU-D"),
    ("VATEX_EU_F", "VATEX-EU-F"),
    ("VATEX_EU_G", "VATEX-EU-G"),
    ("VATEX_EU_I", "VATEX-EU-I"),
    ("VATEX_EU_IC", "VATEX-EU-IC"),
    ("VATEX_EU_J", "VATEX-EU-J"),
    ("VATEX_EU_O", "VATEX-EU-O"),
    ("VATEX_FR-CNWVAT", "VATEX-FR-CNWVAT"),
    ("VATEX_FR-FRANCHISE", "VATEX-FR-FRANCHISE"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr,
        "ubl_cii_tax_exemption_reason_code",
        "ubl_cii_tax_exemption_reason_code",
        _reason_code_map,
        table="account_tax",
    )
