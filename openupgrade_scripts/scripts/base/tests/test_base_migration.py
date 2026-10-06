from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestBaseMigration(TransactionCase):
    def test_ir_access(self):
        """
        Test that manual ir.model.access/ir.rule records have been migrated correctly
        """
        expected_access = (
            (self.env["res.groups"], "r", False),
            (self.env["res.groups"], "d", "[('create_uid', '=', user.id)]"),
            (self.env.ref("base.group_user"), "cru", "[('create_uid', '=', user.id)]"),
            (self.env.ref("base.group_erp_manager"), "u", "[(1, '=', 1)]"),
            (self.env.ref("base.group_system"), "d", "[(1, '=', 1)]"),
            (self.env.ref("base.group_portal"), "ru", "[('create_uid', '=', user.id)]"),
        )
        test_model_access = self.env["ir.access"].search(
            [
                ("model_id.model", "=", "x_v19_base_test_model"),
            ]
        )
        self.assertItemsEqual(
            expected_access,
            test_model_access.mapped(lambda x: (x.group_id, x.operation, x.domain)),
        )

    def test_ir_actions_client(self):
        """
        Test that ir.actions.client#params_store has been converted
        """
        action = self.env["ir.actions.client"].search(
            [("name", "=", "Test action for params_store")]
        )
        self.assertEqual(action.params["some"], "value")

    def test_user_role_assignment(self):
        """
        Test that previous base.group_user members are regular users
        """
        user = self.env["res.users"].search([("login", "=", "test_user_v19")])
        self.assertEqual(user.role, "regular_user")
        self.assertIn(self.env.ref("base.group_user_regular"), user.group_ids)
        self.assertNotIn(
            self.env.ref("base.group_user_regular"),
            self.env.ref("base.user_admin").group_ids,
        )
