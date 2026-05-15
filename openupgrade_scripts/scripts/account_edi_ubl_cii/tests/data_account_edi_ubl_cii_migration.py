# Seed 18.0 demo taxes with each legacy VATEX_* selection value so the
# 19.0 pre-migration has data to rewrite and the post-migration test
# has something to assert. Single-statement SQL avoids odoo-bin shell
# stdin's quirks with indented Python blocks.
env = locals().get("env")
env.cr.execute("""
    WITH legacy(code, rn) AS (VALUES
        ('VATEX_EU_AE', 1), ('VATEX_EU_D', 2), ('VATEX_EU_F', 3),
        ('VATEX_EU_G', 4), ('VATEX_EU_I', 5), ('VATEX_EU_IC', 6),
        ('VATEX_EU_J', 7), ('VATEX_EU_O', 8), ('VATEX_FR-CNWVAT', 9),
        ('VATEX_FR-FRANCHISE', 10)
    ),
    taxes AS (
        SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS rn
        FROM account_tax
        WHERE ubl_cii_tax_exemption_reason_code IS NULL
        LIMIT 10
    )
    UPDATE account_tax SET ubl_cii_tax_exemption_reason_code = legacy.code
    FROM taxes, legacy
    WHERE account_tax.id = taxes.id AND legacy.rn = taxes.rn
""")
env.cr.commit()
