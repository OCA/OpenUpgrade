from odoo.tests import TransactionCase, tagged

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestAccountMigration(TransactionCase):
    def test_fiscal_position(self):
        """
        Test that fiscal positions are migrated correctly
        """
        domestic_tax = self.env.ref("account.1_purchase_tax_template")
        foreign_tax1 = self.env["account.tax"].search([("name", "=", "Foreign tax1")])
        foreign_tax2 = self.env["account.tax"].search([("name", "=", "Foreign tax2")])
        foreign_fpos = self.env["account.fiscal.position"].search(
            [("name", "=", "Foreign fiscal position")]
        )

        self.assertItemsEqual(
            foreign_fpos.map_tax(domestic_tax), foreign_tax1 + foreign_tax2
        )

    def test_exchange_move(self):
        """
        Test that we create a partial reconciliation for the exchange move of a full
        reconciliation if set
        """
        reconciled_move = self.env["account.move"].search(
            [("ref", "=", "Exchange move test move")]
        )
        full_reconcile = reconciled_move.line_ids.full_reconcile_id
        self.assertTrue(full_reconcile)
        exchange_move = self.env["account.move"].search(
            [("ref", "=", "Exchange move of test move's full reconciliation")]
        )
        self.assertTrue(exchange_move)
        self.assertIn(
            exchange_move, full_reconcile.partial_reconcile_ids.exchange_move_id
        )

    def test_reconcile_model_partner_mapping(self):
        """
        Test that for each partner mapping, a new reconcile model was created
        """
        self._test_reconcile_model_partner_mapping(
            "Model with partner mapping, contains label matching",
            "(?=.*hello\\ world.*)(hello)|(world)",
        )
        self._test_reconcile_model_partner_mapping(
            "Model with partner mapping, not_contains label matching",
            "(?!hello\\ world)(hello)|(world)",
        )
        self._test_reconcile_model_partner_mapping(
            "Model with partner mapping, regex label matching",
            "(?=hello world)(hello)|(world)",
        )

    def _test_reconcile_model_partner_mapping(self, name, combined_regex):
        models = self.env["account.reconcile.model"].search(
            [
                ("name", "like", name),
            ]
        )
        self.assertEqual(len(models), 2)
        model_with_mapping = models.filtered("mapped_partner_id")
        self.assertTrue(model_with_mapping)
        self.assertEqual(
            model_with_mapping.match_label_param,
            combined_regex,
        )


@openupgrade_test
@tagged("post_install")
class TestAccountPostMigration(TransactionCase):
    def test_company_accounts(self):
        """
        Test that end-migration has set expense_account_id, income_account_id
        """
        company = self.env.ref("base.main_company")
        self.assertTrue(company.expense_account_id)
        self.assertTrue(company.income_account_id)
