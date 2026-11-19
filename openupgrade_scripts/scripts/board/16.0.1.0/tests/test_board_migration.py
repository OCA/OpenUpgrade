import ast

from lxml import etree

from odoo.tests import TransactionCase


class TestBoardMigration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.custom_view = cls.env["ir.ui.view.custom"].search(
            [("arch", "ilike", "OpenUpgrade Test Dashboard")], limit=1
        )

    def _get_actions(self):
        self.assertTrue(self.custom_view, "The test dashboard is missing")
        return {
            action.get("string"): action
            for action in etree.fromstring(self.custom_view.arch).iter("action")
        }

    def test_dashboard_comparison(self):
        """The 14.0 comparison is converted to the 16.0 search model format."""
        action = self._get_actions()["OpenUpgrade Test Dashboard"]
        context = ast.literal_eval(action.get("context"))
        comparison = context["comparison"]
        self.assertEqual(comparison["fieldName"], "create_date")
        self.assertEqual(
            [domain["description"] for domain in comparison["domains"]],
            ["2023", "2022"],
        )
        for domain, year in zip(comparison["domains"], ("2023", "2022"), strict=True):
            self.assertIn(("is_company", "=", True), domain["arrayRepr"])
            self.assertIn(
                ("create_date", ">=", "%s-01-01 00:00:00" % year),
                domain["arrayRepr"],
            )
            self.assertIn(
                ("create_date", "<=", "%s-12-31 23:59:59" % year),
                domain["arrayRepr"],
            )
        self.assertEqual(context["group_by"], ["create_date:month"])
        self.assertFalse(context["dashboard_merge_domains_contexts"])

    def test_dashboard_without_comparison(self):
        """A dashboard action without a comparison is left untouched."""
        action = self._get_actions()["OpenUpgrade Test Dashboard No Comparison"]
        self.assertEqual(
            ast.literal_eval(action.get("context")),
            {"group_by": ["create_date:month"]},
        )
