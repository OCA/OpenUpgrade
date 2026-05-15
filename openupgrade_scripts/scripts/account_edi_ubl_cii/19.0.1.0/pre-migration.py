from openupgradelib import openupgrade

_VATEX_RENAMES = [
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
    """Migrate 18.0 underscored VATEX codes to the 19.0 hyphenated form
    on account.tax.ubl_cii_tax_exemption_reason_code. Explicit value-by-value
    mapping (not a regex REPLACE) so unrelated codes can never be touched.
    """
    for old, new in _VATEX_RENAMES:
        openupgrade.logged_query(
            env.cr,
            "UPDATE account_tax SET ubl_cii_tax_exemption_reason_code = %s "
            "WHERE ubl_cii_tax_exemption_reason_code = %s",
            (new, old),
        )
