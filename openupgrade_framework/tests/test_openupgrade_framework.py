from odoo import fields
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

    def test_03_update_list(self):
        """
        Test that updating the module list marks uninstalled auto_install modules as
        to install if it's not a localization or country specific with a country not
        in use
        """
        IrModuleModule = self.env["ir.module.module"]
        base = IrModuleModule.create(
            {
                "name": "openupgrade_framework_test_base",
                "state": "installed",
            }
        )
        auto_install = IrModuleModule.create(
            {
                "name": "openupgrade_framework_test_auto_install",
                "state": "uninstalled",
                "auto_install": "true",
                "dependencies_id": [
                    fields.Command.create({"name": base.name}),
                ],
            }
        )
        auto_install_localization = IrModuleModule.create(
            {
                "name": "l10n_openupgrade_framework_localization",
                "state": "uninstalled",
                "auto_install": "true",
                "dependencies_id": [
                    fields.Command.create({"name": base.name}),
                ],
            }
        )
        auto_install_country_specific = IrModuleModule.create(
            {
                "name": "l10n_openupgrade_framework_auto_install_country_specific",
                "state": "uninstalled",
                "auto_install": "true",
                "dependencies_id": [
                    fields.Command.create({"name": base.name}),
                ],
            }
        )
        with mute_logger("odoo.modules.module"):
            self.env["ir.module.module"].update_list()
        self.assertEqual(auto_install.state, "to install")
        self.assertEqual(auto_install_localization.state, "uninstalled")
        self.assertEqual(auto_install_country_specific.state, "uninstalled")
