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

    def test_ir_actions_name_translations(self):
        """The name of the ir.actions.* records keeps its translations.

        Their columns are converted to jsonb keeping only en_US by the ORM, and
        the pre-migration excludes them from the generic translation migration.
        """
        action = self.env["ir.actions.server"].search(
            [("name", "=", "OpenUpgrade Test Action")], limit=1
        )
        self.assertTrue(action, "The test server action is missing")
        self.assertEqual(
            action.with_context(lang="fr_FR").name, "Action de test OpenUpgrade"
        )
        cron = self.env["ir.cron"].search(
            [("ir_actions_server_id", "=", action.id)], limit=1
        )
        self.assertTrue(cron, "The test scheduled action is missing")
        self.assertEqual(
            cron.with_context(lang="fr_FR").name, "Action de test OpenUpgrade"
        )
