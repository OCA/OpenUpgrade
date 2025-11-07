from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestArchFs(TransactionCase):
    def test_arch_fs(self):
        """
        Test that we didn't overwrite arch_fs with the path to the
        noupdate changes file
        """
        self.assertNotIn(
            "openupgrade_scripts",
            self.env.ref("hr_recruitment.candidate_hired_template").arch_fs,
        )
