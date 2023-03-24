from odoo.tests import TransactionCase


class TestBaseMigration(TransactionCase):
    def test_company_registry(self):
        """Make sure we copy res.company#company_registry to res.partner#company_registry"""
        self.assertEqual(self.env.ref("base.main_company").company_registry, "424242")

    def test_translations(self):
        """
        We have a DB with French translations as v15 test db,
        check its translations have been converted correctly
        """
        title_mister = self.env.ref("base.res_partner_title_mister")
        self.assertEqual(title_mister.name, "Mister")
        self.assertEqual(title_mister.with_context(lang="fr_FR").name, "Monsieur")
