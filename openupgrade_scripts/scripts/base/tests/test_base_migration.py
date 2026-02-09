from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestBaseMigration(TransactionCase):
    def test_server_action_child_ids(self):
        """
        Test that server action children are migrated correctly
        """
        action1 = self.env["ir.actions.server"].search(
            [("name", "=", "test server action 1")]
        )
        self.assertTrue(action1)
        self.assertItemsEqual(
            action1.child_ids.mapped("name"), ("child action 1", "child action 2")
        )
        action2 = self.env["ir.actions.server"].search(
            [("name", "=", "test server action 2")]
        )
        self.assertTrue(action2)
        self.assertItemsEqual(
            action2.child_ids.mapped("name"),
            ("child action 1", "child action 2", "child action 3"),
        )
