from odoo.tests.common import TransactionCase
from odoo.tools.misc import mute_logger

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class TestOpenupgradeFramework(TransactionCase):
    def test_01_delete_undeletable_record(self):
        """
        Test that Odoo doesn't crash when deleting records that can't be deleted
        during module upgrade
        """
        with (
            mute_logger("odoo.sql_db"),
            self.assertLogs(
                "odoo.addons.openupgrade_framework.odoo_patch.odoo.orm.models"
            ),
        ):
            self.env.ref("base.partner_admin").with_context(
                **{MODULE_UNINSTALL_FLAG: True}
            ).unlink()

    def test_02_invalid_view(self):
        """
        Test that we patch away fatal view errors and log the problem
        """
        with self.assertLogs(
            "odoo.addons.openupgrade_framework.odoo_patch.odoo.addons.base.models.ir_ui_view"
        ):
            self.env["ir.ui.view"].create(
                {
                    "model": "res.partner",
                    "arch": '<form><field name="nonexisting_field" /></form>',
                }
            )
