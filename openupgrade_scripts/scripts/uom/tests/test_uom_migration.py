from odoo.tests import TransactionCase

from odoo.addons.openupgrade_framework import openupgrade_test


@openupgrade_test
class TestUomMigration(TransactionCase):
    def test_uoms(self):
        """
        Test that decimeters and megameters compute correctly
        """
        dm = self.env["uom.uom"].search([("name", "=", "dm")])
        Mm = self.env["uom.uom"].search([("name", "=", "Mm")])
        self.assertEqual(
            dm._compute_quantity(1, Mm, round=False),
            0.0000001,
        )
        self.assertEqual(
            Mm._compute_quantity(1, dm),
            10000000,
        )
        mA = self.env["uom.uom"].search([("name", "=", "mA")])
        MA = self.env["uom.uom"].search([("name", "=", "MA")])
        self.assertEqual(
            mA._compute_quantity(1, MA, round=False),
            0.000000001,
        )
        self.assertEqual(
            MA._compute_quantity(1, mA),
            1000000000,
        )
