from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestAccountEdiUblCiiMigration(TransactionCase):
    def test_no_legacy_vatex_codes(self):
        """The 18.0 underscored VATEX_* selection values are renamed to the
        19.0 hyphenated VATEX-* form. After migration, no account.tax row
        should still carry a legacy VATEX_ value.
        """
        self.env.cr.execute(
            r"""
            SELECT id FROM account_tax
            WHERE ubl_cii_tax_exemption_reason_code LIKE 'VATEX\_%' ESCAPE '\'
            """
        )
        self.assertEqual(self.env.cr.fetchall(), [])

    def test_new_vatex_codes_present(self):
        """The data_account_edi_ubl_cii_migration.py snippet seeds 18.0 demo
        taxes with the 10 legacy VATEX_* values pre-migration. After
        migration, their hyphenated VATEX-* equivalents must be present.
        """
        new_codes = (
            "VATEX-EU-AE",
            "VATEX-EU-D",
            "VATEX-EU-F",
            "VATEX-EU-G",
            "VATEX-EU-I",
            "VATEX-EU-IC",
            "VATEX-EU-J",
            "VATEX-EU-O",
            "VATEX-FR-CNWVAT",
            "VATEX-FR-FRANCHISE",
        )
        for code in new_codes:
            self.assertTrue(
                self.env["account.tax"].search(
                    [("ubl_cii_tax_exemption_reason_code", "=", code)], limit=1
                ),
                f"Expected at least one account.tax with code {code} after migration.",
            )
