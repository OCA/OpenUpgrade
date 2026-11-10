from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestMailMigration(TransactionCase):
    def test_channel_owner(self):
        """
        Test that channels are assigned owners
        """
        test_channel = self.env["discuss.channel"].search(
            [("name", "=", "OpenUpgrade v20 test channel")]
        )
        self.assertEqual(
            test_channel.channel_member_ids.filtered(
                lambda x: x.partner_id.user_ids.login == "test_user_v19"
            ).channel_role,
            "owner",
        )
