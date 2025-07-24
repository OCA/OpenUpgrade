from odoo.tests import TransactionCase, tagged


@tagged("-at_install", "post_install")
class TestNewlyInstalledEndMigration(TransactionCase):
    def test_newly_installed_end_migration(self):
        """Make sure the code of the end-migration script has been executed"""
        params = self.env["ir.config_parameter"].sudo()
        res = params.get_param("openupgrade.test_end_migration", default="Not executed")
        self.assertEqual(res, "Executed")
